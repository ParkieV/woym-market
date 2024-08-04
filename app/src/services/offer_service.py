from typing import Any

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, Paragraph, SimpleDocTemplate
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.warehouse_db import create_own_storage_stocks
from src.params.confing import config
from logs import get_logger
from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import offer_db as db
from src.database.settings_db import get_markets
import src.services.offer_utils as utils
from src.schemas.base_api_schemas import APIPriceChangeData
from src.schemas.offer_schemas import OfferChange, OfferOut, OfferDelete, ExportType, ImportType, Market, \
    PricingSchemeOut, PricingSchemeCreate, BaseOffer, PricingSchemeFieldCreate, PricingSchemeFieldChange, \
    PricingSchemeChange
import pandas as pd
import numpy as np
from src.database.settings_db import update_logs, get_user_settings
from fastapi.exceptions import HTTPException
from fastapi import status
from datetime import datetime

from src.schemas.settings_schemas import MarketOut
from src.schemas.stocks.own_storages_schemas import OwnStorageCreate
from src.services.base_utils import error_handler


api_wrapper = APIWrapper()

logger = get_logger(__name__)

CONTROL_CHANGES = ['search_words']


async def get_offers(filters: dict[str, Any] | None = None, offset: int = 0, limit: int | None = None) -> list[OfferOut]:
    async with async_session() as session:
        return await db.get_offers(session, filters, offset=offset, limit=limit)


@error_handler('Ошибка изменения товаров')
async def change_offers(offers_data: list[OfferChange], user_id: int):
    mapping_fields = ['sku', 'name_of_shop', 'market']

    if not offers_data:
        return offers_data

    async with async_session() as session:
        settings = await get_user_settings(session, user_id)

        changes = pd.DataFrame([offer.model_dump() for offer in offers_data])
        [await db.check_pricing_schemes_exists(session, i) for i in changes['pricing_scheme_name'].values.tolist()]

        offers_db = await db.get_offers_by(session, changes[mapping_fields].to_dict('records'))
        offers_db_df = pd.DataFrame([i.model_dump() for i in offers_db])[changes.columns.values]

        if len(offers_db_df) != len(changes):
            logger.info('')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Неудалось обновить товары')

        merge_result = pd.merge(offers_db_df[mapping_fields + CONTROL_CHANGES], changes[mapping_fields + CONTROL_CHANGES], on=mapping_fields)
        for field in CONTROL_CHANGES:
            merge_result[f'{field}_changed'] = ~merge_result[f'{field}_x'].eq(merge_result[f'{field}_y'])
            merge_result.drop([f'{field}_x', f'{field}_y'], axis='columns', inplace=True)

        changes = pd.merge(changes, merge_result, on=mapping_fields)

        await db.update_offers(session, changes, mapping_columns=['name_of_shop', 'market'])
        await recalculate_values(session, settings, which=changes[mapping_fields])
        return await db.get_offers_by(session, changes[mapping_fields])


async def setup_offers_data(user_id: int):
    yandex_offers = await api_wrapper.get_offers_list()
    yandex_offers_df = pd.DataFrame(yandex_offers)
    async with async_session() as session:
        await db.check_pricing_schemes_exists(session, 'Y0')
        await db.check_pricing_schemes_exists(session, 'O0')
        settings = await get_user_settings(session, user_id)

        data = await utils.build_offers_data(yandex_offers_df, setup_mode=True, settings=settings)

        offers_db = await db.create_offers(session, data)
        return offers_db


async def update_offers(user_id: int):
    logger.info('Start update offers')
    start_time = datetime.now()

    yandex_offers = await api_wrapper.get_offers_list()
    db_offers = await get_offers()
    offers_df = pd.DataFrame([offer.model_dump() for offer in db_offers])
    yandex_offers_df = pd.DataFrame(yandex_offers)

    mapping_fields = ['sku', 'name_of_shop', 'market']

    offers_db_identifiers = set([tuple(i.values()) for i in offers_df[mapping_fields].to_dict('records')])
    yandex_offers_identifiers = set([tuple(i.values()) for i in yandex_offers_df[mapping_fields].to_dict('records')])

    to_update = offers_db_identifiers & yandex_offers_identifiers
    to_create = yandex_offers_identifiers - offers_db_identifiers
    to_delete = offers_db_identifiers - yandex_offers_identifiers

    to_update_df = pd.merge(yandex_offers_df, pd.DataFrame(to_update, columns=mapping_fields), how='inner')
    to_update_df[['best_place_wm', 'best_place_im', 'photo']] = to_update_df[['best_place_wm', 'best_place_im', 'photo']].astype('string')
    to_create_df = pd.merge(yandex_offers_df, pd.DataFrame(to_create, columns=mapping_fields), how='inner')

    to_delete_df = pd.DataFrame(to_delete, columns=mapping_fields)

    async with async_session() as session:
        to_update_price_df = offers_df.copy()
        merge_result = pd.merge(to_update_price_df[mapping_fields + CONTROL_CHANGES + [f'{i}_changed' for i in CONTROL_CHANGES]], yandex_offers_df[mapping_fields + CONTROL_CHANGES], on=mapping_fields)

        # Логика для двухсторонней синхронизации полей (наши изменения в приоритете)
        for column in CONTROL_CHANGES:
            merge_result[column] = np.where(
                merge_result[f'{column}_changed'],
                merge_result[f'{column}_x'],
                merge_result[f'{column}_y']
            )
            merge_result.drop([f'{column}_x', f'{column}_y'], axis='columns', inplace=True)
        to_update_price_df.drop(CONTROL_CHANGES + [f'{i}_changed' for i in CONTROL_CHANGES], axis='columns', inplace=True)
        to_update_price_df = pd.merge(merge_result, to_update_price_df, on=mapping_fields)

        # Обновление цен
        await update_offers_price(to_update_price_df[to_update_price_df['auto_price_control'] == True])
        settings = await get_user_settings(session, user_id)

        # Создание новых товаров
        for market in await get_markets(session):
            to_create_df_chunked = await utils.build_offers_data(to_create_df[((to_create_df['market'] == market.type) & (to_create_df['name_of_shop'] == market.name))], settings, market, setup_mode=True)
            await db.create_offers(session, to_create_df_chunked)

        await create_own_storage_stocks(session)

        # Снять галочки с измененных полей
        for column in CONTROL_CHANGES:
            to_update_df[f'{column}_changed'] = False

        await db.update_offers(session, to_update_df, mapping_columns=['name_of_shop', 'market'])
        await db.delete_offers(session, to_delete_df)
        await recalculate_values(session, settings)

        await update_logs(session, user_id, {'updated_at': datetime.now()})

    _time = datetime.now() - start_time
    logger.info(f'Offers update completed in {_time}')


async def delete_offers(offers: list[OfferDelete]):
    async with async_session() as session:
        return await db.delete_offers(session, [offer.model_dump() for offer in offers])


async def update_offers_price(offers: pd.DataFrame | list[OfferOut]):
    data = []

    if isinstance(offers, pd.DataFrame):
        data = offers.to_dict('records')
    elif isinstance(offers, list):
        data = [i.model_dump() for i in offers]

    if not len(data):
        logger.warning('Price update list is empty')

    data = [
        APIPriceChangeData(
            sku=offer_data['sku'],
            market=offer_data['market'],
            name_of_shop=offer_data['name_of_shop'],
            target_price=offer_data['target_price'],
            min_price=offer_data['manual_min_price'] if offer_data['use_manual_min_price'] else offer_data['total_price'] * offer_data['auto_min_price'] / 100,
            auto_participation_in_promotions=offer_data['auto_participation_in_promotions'],
            auto_min_price=offer_data['target_price'] * offer_data['auto_min_price'] / 100 if all((offer_data['target_price'], offer_data['auto_min_price'])) else None,
            search_words=offer_data['search_words']
        )
        for offer_data in data if offer_data['total_price'] is not None
    ]

    if config.is_dev:
        return

    await api_wrapper.change_prices(data)


async def recalculate_values(session: AsyncSession, settings, which=None):
    if which is None:
        offers = await db.get_offers(session, model_schema=OfferOut)
    else:
        offers = await db.get_offers_by(session, which, model_schema=OfferOut)

    df = pd.DataFrame([offer.model_dump() for offer in offers])
    df.drop('dollar_cost_price_updated_at', axis=1, inplace=True, errors='ignore')
    df.fillna(np.nan, inplace=True)
    df.drop('dollar_cost_price_updated_at', axis=1, inplace=True, errors='ignore')

    if df.empty:
        return

    # df = await utils.calculate_offers_values(df, settings)

    for market in await get_markets(session):
        df1 = await utils.calculate_offers_values(df[((df['name_of_shop'] == market.name) & (df['market'] == market.type))], settings, market)
        df1.drop(set(df1.columns) - set(OfferOut.fields()), axis=1, inplace=True, errors='ignore')

        await db.update_offers(session, df1, mapping_columns=['sku', 'name_of_shop'])
from functools import lru_cache

@error_handler('Ошибка импорта')
async def import_data(data: bytes, market: Market, import_type: ImportType, name_of_shop: str | None, user_id: int, file_extension: str = 'xlsx') -> None:
    async with async_session() as session:
        settings = await get_user_settings(session, user_id)

    match import_type:
        case ImportType.TABLE:
            return await import_offers(data, settings, name_of_shop, market, file_extension)

        case ImportType.SIZES:
            return await import_sizes(data, settings, name_of_shop, market, file_extension)

        case ImportType.PRICES:
            return await import_prices(data, settings, name_of_shop, market, file_extension)

        case _:
            raise NotImplemented(f'Import type "{import_type}" not implemented yet')


async def import_offers(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    required_fields = {'sku', 'market', 'name_of_shop'}

    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df.fillna({
        'note_1': '',
        'note_2': '',
        'note_3': '',
    }, inplace=True)

    if len(set(df.columns) & required_fields) != len(required_fields):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные. Следующие колонки должны быть обязательно: {", ".join(BaseOffer.fields().values())}')

    if name_of_shop:
        df = df[df['name_of_shop'] == name_of_shop]

    if market:
        df = df[df['market'] == market]

    columns_to_change = list(set(df.columns) & set(OfferChange.fields().keys()))
    df = df[columns_to_change]

    df[['sku', 'name_of_shop', 'market', 'note_1', 'note_2', 'note_3']] = df[['sku', 'name_of_shop', 'market', 'note_1', 'note_2', 'note_3']].astype("string")

    async with async_session() as session:
        if 'pricing_scheme_name' in df.columns:
            [await db.check_pricing_schemes_exists(session, i) for i in set(df['pricing_scheme_name'].values.tolist())]

        try:
            await db.update_offers(session, df, mapping_columns=['name_of_shop', 'market'], endswith_sku=False)
        except Exception as e:
            print(e)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные.')

        await recalculate_values(session, settings, df[['sku', 'name_of_shop', 'market']])


async def import_prices(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.drop(df.columns[[3, 4, 6, 7]], axis=1, inplace=True, errors='ignore')
    df.drop([i for i in range(8)], axis=0, inplace=True, errors='ignore')
    df.columns = ['sku', 'name', 'discount_price', 'price']

    df['sku'] = df['sku'].astype('string')

    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    df['use_promotion_price'] = df['discount_price'].notna()
    df['wholesale_dollar_cost_price'] = df['price']

    async with async_session() as session:
        for _market in await get_markets(session, MarketOut):
            if name_of_shop is not None and name_of_shop != _market.name:
                continue

            if market is not None and _market.type != market:
                continue

            chunked_df = df.copy()

            chunked_df['wholesale_dollar_cost_price'] = np.where(
                chunked_df['use_promotion_price'],
                chunked_df['discount_price'],
                chunked_df['wholesale_dollar_cost_price']
            )
            chunked_df.drop(['name', 'discount_price', 'price'], axis=1, inplace=True)
            chunked_df['market'] = _market.type
            chunked_df['name_of_shop'] = _market.name
            # Зависит от магазина
            await db.update_offers(session, chunked_df, mapping_columns=['market', 'name_of_shop'], endswith_sku=True)

            db_skus = set([i.lstrip('0') for i in await db.get_unique_skus(session)])
            import_skus = set(chunked_df['sku'].values.tolist())

            await db.set_supplier_available(session, db_skus & import_skus, True)
            await db.set_supplier_available(session, db_skus - import_skus, False)

        now = datetime.now()
        await db.set_dollar_cost_price_updated_at(session, import_skus, now)
        await recalculate_values(session, settings)


async def import_sizes(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, 'Список товаров', file_extension)
    df.drop([0, 1], axis=0, inplace=True, errors='ignore')
    df: pd.DataFrame = df[df.columns[[2, 13, 14]]]
    df.columns = ['sku', 'self_weight', 'sizes']
    df[['self_length', 'self_width', 'self_height']] = df['sizes'].str.split('/', expand=True)
    df[['self_length', 'self_width', 'self_height', 'self_weight']] = df[
        ['self_length', 'self_width', 'self_height', 'self_weight']].astype(float)
    df['volume'] = df['self_length'] * df['self_width'] * df['self_height'] / 1000
    df['sku'] = df['sku'].astype('string')

    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    df.fillna(0, inplace=True)
    df.drop('sizes', axis=1, inplace=True)

    mapping_columns = []

    if name_of_shop:
        df['name_of_shop'] = name_of_shop
        mapping_columns.append('name_of_shop')

    if market:
        df['market'] = market
        mapping_columns.append('market')

    async with async_session() as session:
        try:
            await db.update_offers(session, df, mapping_columns=mapping_columns, endswith_sku=True)
        except Exception as e:
            print(e)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные.')

        await recalculate_values(session, settings)


async def export_offers(name_of_shop: str | None = None, market: str | None = None) -> str:
    filters = {}

    if name_of_shop:
        filters['name_of_shop'] = name_of_shop

    if market:
        filters['market'] = market

    offers = await get_offers(filters)

    df = pd.DataFrame([offer.model_dump() for offer in offers], columns=OfferOut.fields().keys())
    df['dollar_cost_price_updated_at'] = df['dollar_cost_price_updated_at'].astype('string')
    df['dollar_cost_price_updated_at'].fillna('', inplace=True)
    df['dollar_cost_price_updated_at'] = df['dollar_cost_price_updated_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y') if x else x)
    df.rename(columns=OfferOut.fields(), inplace=True)
    df.to_excel('data/out-offers.xlsx', index=False)
    return 'data/out-offers.xlsx'


async def get_pricing_schemes() -> list[PricingSchemeOut]:
    async with async_session() as session:
        return await db.get_pricing_schemes(session)


async def create_pricing_scheme(data: PricingSchemeCreate) -> PricingSchemeOut:
    async with async_session() as session:
        return await db.create_pricing_scheme(session, data)


@error_handler('Не удалось обновить данные')
async def change_pricing_scheme(user_id: int, data: PricingSchemeChange):
    async with async_session() as session:
        settings = await get_user_settings(session, user_id)

        await db.change_pricing_scheme(session, data)
        await recalculate_values(session, settings, which=[{'pricing_scheme_name': data.name}])


async def delete_pricing_scheme(names: list[str]):
    async with async_session() as session:
        await db.delete_pricing_scheme(session, names)


async def change_pricing_scheme_field(data: list[PricingSchemeFieldChange]):
    async with async_session() as session:
        await db.change_pricing_scheme_field(session, data)


async def create_pricing_scheme_field(data: PricingSchemeFieldCreate):
    async with async_session() as session:
        return await db.create_pricing_scheme_field(session, data)


async def delete_pricing_schemes(data: list[str]) -> None:
    async with async_session() as session:
        await db.delete_pricing_scheme(session, data)


async def delete_pricing_scheme_fields(ids: list[int]) -> None:
    async with async_session() as session:
        await db.delete_pricing_scheme_fields(session, ids)


async def create_violators_file(market: Market | None = None, name_of_shop: str | None = None) -> str:
    async with async_session() as session:
        violators = await db.get_violators(session, market=market, name_of_shop=name_of_shop)

        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'DejaVuSerif'
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'src/DejaVuSerif.ttf', 'UTF-8'))

        if len(violators):
            f = [
                Paragraph(f'{i+1}. SKU: {violator.sku}, Маркетплейс: {violator.market}, Магазин: {violator.name_of_shop}, Цена: {round(violator.price)}, РРЦ: {round(violator.recommended_retail_price)}', style=ParagraphStyle('ParStyles', fontName='DejaVuSerif', leading=20))
                for i, violator in enumerate(violators)]
        else:
            f = [Paragraph('Нарушителей не найдено.', style=ParagraphStyle('ParStyles', fontName='DejaVuSerif', leading=20))]
        canvas = SimpleDocTemplate("data/violators.pdf", )
        canvas.build(f)

        return "data/violators.pdf"

