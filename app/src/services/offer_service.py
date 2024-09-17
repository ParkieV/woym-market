from typing import Any

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from sqlalchemy.ext.asyncio import AsyncSession

import src.services.base_utils
from src.database.catalog_db import sync_catalog_items_with_offers, reverse_sync_offers_with_catalog_items
from src.database.models.models import Offer
from src.database.warehouse_db import create_own_storage_stocks
from src.params.confing import config
from logs import get_logger
from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import offer_db as db
from src.database.settings_db import get_markets
import src.services.offer_utils as utils
from src.schemas.base_api_schemas import APIPriceChangeData, APIOfferChangeData
from src.schemas.filters.filter_schemas import PagingFilter
from src.schemas.filters.offers_filter import OffersFilter
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

CONTROL_CHANGES = ['search_words', 'description', 'name', 'barcodes', 'self_weight', 'self_length', 'self_width', 'self_height']


async def get_offers_list(offers_filter: OffersFilter | None = None, paging_filter: PagingFilter | None = None) -> list[OfferOut]:
    async with async_session() as session:
        return await db.get_offers_list(session, paging=paging_filter, offers_filter=offers_filter)


@error_handler('Ошибка изменения товаров')
async def change_offers(offers: list[OfferChange], user_id: int):
    if not offers:
        return offers

    async with async_session() as session:
        settings = await get_user_settings(session, user_id)
        offers_data = [i.model_dump(exclude_unset=True) for i in offers]
        await db.change_offers(session, offers=offers_data, mapping_fields=['id'], detect_changes=['name', 'description', 'barcodes', 'search_words', 'self_weight', 'self_length', 'self_width', 'self_height'])
        await recalculate_values(session, settings, offers_filter=OffersFilter(offer_ids=[i.id for i in offers]))


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
    mapping_fields = ['sku', 'name_of_shop', 'market']
    start_time = datetime.now()

    async with async_session() as session:
        markets = await get_markets(session)
        settings = await get_user_settings(session, user_id)

        await reverse_sync_offers_with_catalog_items(session)
        logger.info('Reverse sync completed')
        await sync_catalog_items_with_offers(session)
        logger.info('Direct sync sync completed')
        await recalculate_values(session, settings, offers_filter=OffersFilter(synchronization=True))

    # Получаем товары из бд
    db_offers = await get_offers_list()
    db_offers_df = pd.DataFrame([offer.model_dump() for offer in db_offers])

    # Создаем переменную с данными для отправки цен в апи
    to_update_price_df = db_offers_df.copy()

    # Считаем значения, которые требуют настроек и целевой цены
    for market in markets:
        to_update_price_df['discount_base_price'] = np.where(
            (to_update_price_df['market'] == market.type) & (to_update_price_df['name_of_shop'] == market.name),
            to_update_price_df['target_price'] * (1.0 + market.price_before_discount / 100),
            to_update_price_df['discount_base_price']
        )

    # Обновление цен
    await update_offers_price(to_update_price_df[to_update_price_df['auto_price_control'] == True])

    # Получаем товары из апи
    api_offers = await api_wrapper.get_offers_list()
    api_offers_df = pd.DataFrame(api_offers)

    common_columns = (set(db_offers_df.columns.tolist()) & set(api_offers_df.columns.tolist())) - set(mapping_fields)
    merged_offers = pd.merge(db_offers_df, api_offers_df, on=mapping_fields, how='outer', indicator=True, suffixes=(None, '__api'))

    to_update_offers = merged_offers[merged_offers['_merge'] == 'both']
    to_delete_offers = merged_offers[merged_offers['_merge'] == 'left_only']
    to_create_offers = merged_offers[merged_offers['_merge'] == 'right_only']
    to_create_offers = (
        to_create_offers
        .drop(columns=common_columns)
        .drop(columns=['_merge', 'id'], errors='ignore')
        .rename(columns={f'{column}__api': column for column in common_columns})[api_offers_df.columns.tolist()]
    )

    # Двойная синхронизаия полей
    for tracked_column in CONTROL_CHANGES:
        to_update_offers[tracked_column] = np.where(
            to_update_offers[f'{tracked_column}_changed'],
            to_update_offers[tracked_column],
            to_update_offers[f'{tracked_column}__api']
        )

    # Обновляем атрибуты у тех товаров, в которых были изменения по полям для двойной синхронизации
    to_update_attributes = to_update_offers.query(' | '.join([f'{i}_changed' for i in CONTROL_CHANGES]))
    logger.info(f'Found offers to update attributes: {len(to_update_attributes)}')
    await update_offers_attributes(to_update_attributes)

    # Создаем новые товары
    for market in markets:
        to_create_df_chunked = await utils.build_offers_data(to_create_offers[((to_create_offers['market'] == market.type) & (to_create_offers['name_of_shop'] == market.name))], settings, market, setup_mode=True)
        await db.create_offers(session, to_create_df_chunked)
        logger.info(f'New offers for {market.name}({market.type}) created: {len(to_create_df_chunked)}')


    # Создать новые товары в моих остатках
    await create_own_storage_stocks(session)
    logger.info('Own storage stocks created')

    # Обновляем товары из апи
    api_offers = await api_wrapper.get_offers_list()
    api_offers_df = pd.DataFrame(api_offers)

    for tracked_column in CONTROL_CHANGES:
        api_offers_df[f'{tracked_column}_changed'] = False

    api_offers_df.replace({np.nan: None}, inplace=True)

    # await db.update_offers(session, api_offers_df, mapping_columns=['name_of_shop', 'market'])
    await db.change_offers(session, offers=api_offers_df.to_dict('records'), mapping_fields=['sku', 'market', 'name_of_shop'])
    logger.info(f'Updated db offers: {len(api_offers_df)}')

    # Удаляем товары
    logger.warning(f"Offers to delete: {len(to_delete_offers)} \n{to_delete_offers[['sku', 'market', 'name_of_shop']].to_dict('records')}")

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
        logger.info(f'Skip update offers prices app mode is not PROD (current - {config.mode})')
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
            vendor_code=int(offer_data['vendor_code']) if offer_data['vendor_code'] is not None and not np.isnan(
                offer_data['vendor_code']) else None,
            discount_base_price=offer_data['discount_base_price']

        )
        for offer_data in data if offer_data['total_price'] is not None
    ]

    await api_wrapper.change_prices(data)


async def update_offers_attributes(offers: pd.DataFrame) -> None:
    data = offers.to_dict('records')

    if not config.is_prod:
        logger.info(f'Skip update offers attributes app mode is not PROD (current - {config.mode})')
        return

    if not len(data):
        logger.info('Skip update offers attributes due to list is empty')
        return

    data = [APIOfferChangeData(**offer_data) for offer_data in data]
    await api_wrapper.change_offers(data)


async def recalculate_values(session: AsyncSession, settings, offers_filter: OffersFilter | None = None):
    offers = await db.get_offers_list(session, offers_filter=offers_filter)

    df = pd.DataFrame([offer.model_dump() for offer in offers])
    df.drop('dollar_cost_price_updated_at', axis=1, inplace=True, errors='ignore')
    df.fillna(np.nan, inplace=True)
    df.drop('dollar_cost_price_updated_at', axis=1, inplace=True, errors='ignore')

    if df.empty:
        return

    for market in await get_markets(session):
        df1 = await utils.calculate_offers_values(df[((df['name_of_shop'] == market.name) & (df['market'] == market.type))], settings, market)
        df1.replace({np.nan: None}, inplace=True)
        exclude_columns = set(df1.columns.values.tolist()) - set(i.name for i in Offer.__table__.columns)
        df1.drop(columns=exclude_columns, inplace=True)
        await db.change_offers(session, offers=df1.to_dict('records'), mapping_fields=['id'])


@error_handler('Ошибка импорта')
async def import_data(data: bytes, market: Market, import_type: ImportType, name_of_shop: str | None, user_id: int, file_extension: str = 'xlsx') -> None:
    async with async_session() as session:
        settings = await get_user_settings(session, user_id)

    match import_type:
        case ImportType.TABLE:
            return await import_offers(data, settings, name_of_shop, market, file_extension)

        case ImportType.SIZES:
            return await import_sizes(data, settings, name_of_shop, file_extension)

        case ImportType.PRICES:
            return await import_prices(data, settings, name_of_shop, market, file_extension)

        case _:
            raise NotImplemented(f'Import type "{import_type}" not implemented yet')


async def import_offers(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = src.services.base_utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df.fillna({
        'note_1': '',
        'note_2': '',
        'note_3': '',
    }, inplace=True)
    df['sku'] = df['sku'].astype('string')

    if 'id' not in df.columns.values.tolist():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Колонка id должна присутствовать в файле')

    if name_of_shop:
        df = df[df['name_of_shop'] == name_of_shop]

    if market:
        df = df[df['market'] == market]

    to_update_offers = [OfferChange(**i) for i in df.to_dict(orient='records')]

    async with async_session() as session:
        if 'pricing_scheme_name' in df.columns:
            [await db.check_pricing_schemes_exists(session, i) for i in set(df['pricing_scheme_name'].values.tolist())]

        try:
            await db.change_offers(session, [i.model_dump(exclude_unset=True) for i in to_update_offers], mapping_fields=['id'])
        except Exception as e:
            logger.error('Error while updating offers in import offers', exc_info=e)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные.')

        await recalculate_values(session, settings, offers_filter=OffersFilter(offer_ids=df['id'].values.tolist()))


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
            await db.update_offers_from_list(session, [OfferChange(**i) for i in chunked_df.to_dict('records')])

            db_skus = set([i.lstrip('0') for i in await db.get_unique_skus(session)])
            import_skus = set(chunked_df['sku'].values.tolist())

            await db.set_supplier_available(session, db_skus & import_skus, True)
            await db.set_supplier_available(session, db_skus - import_skus, False)

        await recalculate_values(session, settings)


async def import_sizes(data, settings, name_of_shop: str | None = None, file_extension: str = 'xlsx'):
    df = parce_sizes_list(data, file_extension=file_extension)

    if name_of_shop:
        df['name_of_shop'] = name_of_shop

    df['market'] = 'yandex'

    async with async_session() as session:
        try:
            await db.update_offers_from_list(session, [OfferChange(**i) for i in df.to_dict('records')])
        except Exception as e:
            logger.error('Error while update price in import sizes', exc_info=True)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Некоректные данные.')

        await recalculate_values(session, settings, offers_filter=OffersFilter(market='yandex'))


async def export_offers(offers_filter: OffersFilter | None = None) -> str:

    offers = await get_offers_list(offers_filter=offers_filter)
    exclude_columns = []
    exclude_columns.extend([f'{i}_changed' for i in CONTROL_CHANGES])

    df = pd.DataFrame([offer.model_dump(exclude=exclude_columns) for offer in offers])
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
        await recalculate_values(session, settings, offers_filter=OffersFilter(pricing_scheme_name=data.name))


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

