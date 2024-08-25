from typing import Any

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from sqlalchemy.ext.asyncio import AsyncSession

import src.services.base_utils
from src.database.catalog_db import sync_catalog_items_with_offers
from src.database.warehouse_db import create_own_storage_stocks
from src.params.confing import config
from logs import get_logger
from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import offer_db as db
from src.database.settings_db import get_markets
import src.services.offer_utils as utils
from src.schemas.base_api_schemas import APIPriceChangeData, APIOfferChangeData
from src.schemas.offer_schemas import OfferChange, OfferOut, OfferDelete, ImportType, Market, \
    PricingSchemeOut, PricingSchemeCreate, BaseOffer, PricingSchemeFieldCreate, PricingSchemeFieldChange, \
    PricingSchemeChange
import pandas as pd
import numpy as np
from src.database.settings_db import update_logs, get_user_settings
from fastapi.exceptions import HTTPException
from fastapi import status
from datetime import datetime
from src.services.base_utils import parce_sizes_list, parce_purchase_list
from src.schemas.settings_schemas import MarketOut
from src.services.base_utils import error_handler


api_wrapper = APIWrapper()

logger = get_logger(__name__)

CONTROL_CHANGES = ['search_words', 'description', 'name', 'barcodes']


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

        await db.update_offers(session, changes, mapping_columns=['name_of_shop', 'market'], detect_changes=['name', 'description', 'barcodes', 'search_words'])
        await sync_catalog_items_with_offers(session)
        await recalculate_values(session, settings, which=changes[mapping_fields])


async def setup_offers_data(user_id: int):
    yandex_offers = await api_wrapper.get_offers_list()
    yandex_offers_df = pd.DataFrame(yandex_offers)
    async with async_session() as session:
        await db.check_pricing_schemes_exists(session, 'Y0')
        await db.check_pricing_schemes_exists(session, 'O0')
        await db.check_pricing_schemes_exists(session, 'W0')
        settings = await get_user_settings(session, user_id)

        for market in await get_markets(session):
            data = await utils.build_offers_data(yandex_offers_df[((yandex_offers_df['market'] == market.type) & (yandex_offers_df['name_of_shop'] == market.name))], setup_mode=True, settings=settings, market=market)
            await db.create_offers(session, data)
            logger.info(f'{market.type}({market.name}) offers created: {len(data)}')


async def update_offers(user_id: int):
    logger.info('Start update offers')
    start_time = datetime.now()

    # Синхронизируем данные с каталогом
    async with async_session() as session:
        await sync_catalog_items_with_offers(session)

    # Получаем товары из бд
    db_offers = await get_offers()
    offers_df = pd.DataFrame([offer.model_dump() for offer in db_offers])

    # Получаем товары из апи
    yandex_offers = await api_wrapper.get_offers_list()
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
        # В полях с двойной синхронизации берем наши, если были изменены, иначе из апи
        merge_df = pd.merge(to_update_df, offers_df[mapping_fields + CONTROL_CHANGES + [f'{i}_changed' for i in CONTROL_CHANGES] + ['auto_price_control']], on=mapping_fields, how='inner')
        for column in CONTROL_CHANGES:
            merge_df[column] = np.where(
                merge_df[f'{column}_changed'],
                merge_df[f'{column}_y'],
                merge_df[f'{column}_x']
            )
            merge_df.drop([f'{column}_x', f'{column}_y'], axis='columns', inplace=True)

        to_update_df = merge_df.copy()

        # Обновление характеристик товаров (только измененные)
        to_update_attributes = to_update_df.query(' | '.join([f'{i}_changed' for i in CONTROL_CHANGES]))
        await update_offers_attributes(to_update_attributes)

        # Обновление цен
        await update_offers_price(offers_df[offers_df['auto_price_control'] == True])
        settings = await get_user_settings(session, user_id)

        # После обновление аттрибутов у товаров, которые требовали изменений, выставить маркеры полей в нейтральные
        for column in CONTROL_CHANGES:
            to_update_df[f'{column}_changed'] = False

        # Создание новых товаров
        for market in await get_markets(session):
            to_create_df_chunked = await utils.build_offers_data(to_create_df[((to_create_df['market'] == market.type) & (to_create_df['name_of_shop'] == market.name))], settings, market, setup_mode=True)
            await db.create_offers(session, to_create_df_chunked)
            logger.info(f'New offers for {market.name}({market.type}) created: {len(to_create_df)}')

        # Создать новые товары в моих остатках
        await create_own_storage_stocks(session)
        logger.info('Own storage stocks created')

        # Снять галочки с измененных полей
        for column in CONTROL_CHANGES:
            to_update_df[to_update_df['auto_price_control'] == True][f'{column}_changed'] = False

        await db.update_offers(session, to_update_df, mapping_columns=['name_of_shop', 'market'])
        logger.info(f'Offers updated: {len(to_update_df)}')

        # Удалить товары
        await db.delete_offers(session, to_delete_df)
        logger.info(f'Offers deleted: {len(to_delete_df)}')

        # Синхронизировать товары с каталогом
        await sync_catalog_items_with_offers(session)
        logger.info('Offers synchronized with catalog')

        # Пересчитать все
        await recalculate_values(session, settings)
        logger.info('Offers recalculated')

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

    if not config.is_prod:
        logger.info(f'Skip update offers attributes app mode is not PROD (current - {config.mode})')
        return

    if not len(data):
        logger.info('Skip update prices due to list is empty')
        return

    data = [
        APIPriceChangeData(
            sku=offer_data['sku'],
            market=offer_data['market'],
            name_of_shop=offer_data['name_of_shop'],
            target_price=offer_data['target_price'],
            min_price=offer_data['manual_min_price'] if offer_data['use_manual_min_price'] else offer_data['total_price'] * offer_data['auto_min_price'] / 100,
            auto_participation_in_promotions=offer_data['auto_participation_in_promotions'],
            auto_min_price=offer_data['target_price'] * offer_data['auto_min_price'] / 100 if all((offer_data['target_price'], offer_data['auto_min_price'])) else None,
            vendor_code=offer_data['vendor_code']
        )
        for offer_data in data if offer_data['total_price'] is not None
    ]



    await api_wrapper.change_prices(data)


async def update_offers_attributes(offers: pd.DataFrame):
    data = offers.to_dict('records')

    if not config.is_prod:
        logger.info(f'Skip update offers attributes app mode is not PROD (current - {config.mode})')
        return

    if not len(data):
        logger.info('Skip update offers attributes due to list is empty')
        return

    data = [
        APIOfferChangeData(
            sku=offer_data['sku'],
            market=offer_data['market'],
            name_of_shop=offer_data['name_of_shop'],
            search_words=offer_data['search_words'],
            name=offer_data['name'],
            description=offer_data['description'],
            barcodes=offer_data['barcodes'],
            vendor_code=offer_data['vendor_code']
        )
        for offer_data in data
    ]
    return data


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

    for market in await get_markets(session):
        df1 = await utils.calculate_offers_values(df[((df['name_of_shop'] == market.name) & (df['market'] == market.type))], settings, market)
        df1.drop(set(df1.columns) - set(OfferOut.fields()), axis=1, inplace=True, errors='ignore')

        await db.update_offers(session, df1, mapping_columns=['sku', 'name_of_shop', 'market'])


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

    df = src.services.base_utils.bytes_to_data_frame(data, file_extension=file_extension)
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
            logger.error('Error while updating offers in import offers', exc_info=e)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные.')

        await recalculate_values(session, settings, df[['sku', 'name_of_shop', 'market']])


async def import_prices(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = parce_purchase_list(data, file_extension=file_extension)

    async with async_session() as session:
        for _market in await get_markets(session, MarketOut):
            if name_of_shop is not None and name_of_shop != _market.name:
                continue

            if market is not None and _market.type != market:
                continue

            chunked_df = df.copy()

            chunked_df['market'] = _market.type
            chunked_df['name_of_shop'] = _market.name

            # Зависит от магазина
            await db.update_offers(session, chunked_df, mapping_columns=['market', 'name_of_shop'], endswith_sku=True)

            db_skus = set([i.lstrip('0') for i in await db.get_unique_skus(session)])
            import_skus = set(chunked_df['sku'].values.tolist())

            await db.set_supplier_available(session, db_skus & import_skus, True)
            await db.set_supplier_available(session, db_skus - import_skus, False)

        await recalculate_values(session, settings)


async def import_sizes(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = parce_sizes_list(data, file_extension=file_extension)

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
            logger.error('Error while update price in import sizes', exc_info=True)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные.')

        await recalculate_values(session, settings)


async def export_offers(name_of_shop: str | None = None, market: str | None = None) -> str:
    filters = {}

    if name_of_shop:
        filters['name_of_shop'] = name_of_shop

    if market:
        filters['market'] = market

    offers = await get_offers(filters)

    exclude_columns = [f'{i}_changed' for i in CONTROL_CHANGES]

    df = pd.DataFrame([offer.model_dump() for offer in offers], columns=OfferOut.fields().keys())
    df['dollar_cost_price_updated_at'] = df['dollar_cost_price_updated_at'].astype('string')
    df['dollar_cost_price_updated_at'].fillna('', inplace=True)
    df['dollar_cost_price_updated_at'] = df['dollar_cost_price_updated_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y') if x else x)
    df.drop(columns=exclude_columns, errors='ignore', inplace=True)
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

