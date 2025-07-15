from datetime import datetime
from typing import Sequence

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from sqlalchemy.ext.asyncio import AsyncSession

import src.services.base_utils
from src.api.interfaces import IApiSessionFabric, ApiTypes
from src.database.interfaces import IDbSessionFabric
from src.database.models.models import Offer, CatalogItem
from src.database.offer import OfferRepository
from src.database.warehouse_db import create_own_storage_stocks
from src.params.config import config
from logs import backend_logger
from src.api.wrapper import ApiInteractor
from src.database.db import async_session, get_db_session
from src.database import offer as db
from src.database.settings_db import get_markets
import src.services.offer_utils as utils
from src.schemas.base_api_schemas import APIPriceChangeData, APIOfferChangeData
from src.schemas.filters.offers_filter import OffersFilter
from src.schemas.offer_schemas import OfferChange, OfferOut, OfferDelete, ImportType, Market, \
    PricingSchemeOut, PricingSchemeCreate, BaseOffer, PricingSchemeFieldCreate, PricingSchemeFieldChange, \
    PricingSchemeChange
import pandas as pd
import numpy as np
from src.database.settings_db import update_logs, get_user_settings
from fastapi.exceptions import HTTPException
from fastapi import status
from src.services.db_metadata import DBMetadataService
from src.services.base_utils import parce_sizes_list, parce_purchase_list
from src.schemas.settings_schemas import MarketOut
from src.services.base_utils import error_handler
from src.services.seller_discount import get_seller_discount_from_page, update_discounts, update_api_discounts
from src.services.synchronization import ReverseSynchronizationInteractor, SynchronizationInteractor
from src.services.update_offer_from_api import UpdateOfferFromApi



CONTROL_CHANGES = (
    'search_words',
    'description',
    'name',
    'barcodes',
    'self_height',
    'self_weight',
    'self_width',
    'self_length'
)

async def get_offers_list(session_fabric: IDbSessionFabric, offers_filter: OffersFilter | None = None) -> list[OfferOut]:
    """ Получение списка карточек """
    res = []
    offer_repository = OfferRepository[OfferOut]()

    async with session_fabric() as session:
        offer_repository.session = session
        async for offer_chunk in offer_repository.offer_list(query_filter=offers_filter):
            res += offer_chunk

    return res


async def change_offers(offers_data: list[OfferChange],
                        user_id: int,
                        session_fabric: IDbSessionFabric):
    """ Функция для изменения данных в карточках товаров """

    if not offers_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No offers to save')

    async with session_fabric() as session:
        await get_user_settings(session, user_id)

        backend_logger.info(f'offer for change: {offers_data[0]}')
        changes = pd.DataFrame([offer.model_dump() for offer in offers_data])

        await db.update_offers(session, changes, mapping_columns=['name_of_shop', 'market'], detect_changes=['name', 'description', 'barcodes', 'search_words'])

        to_sync_skus = [i.sku for i in offers_data if i.synchronization]
        sync_interactor = SynchronizationInteractor(
            DBMetadataService({'Offer': Offer, 'CatalogItem': CatalogItem}),
            session_fabric
        )
        if to_sync_skus:
            await sync_interactor(skus=to_sync_skus)
        await recalculate_values(session)


async def setup_offers_data(api_session_fabric: IApiSessionFabric,
                            db_session_fabric: IDbSessionFabric,):
    api_interactor = ApiInteractor(api_session_fabric=api_session_fabric,
                                   db_session_fabric=db_session_fabric)
    yandex_offers = await api_interactor.get_offers_list()
    yandex_offers_df = pd.DataFrame(yandex_offers)
    async with async_session() as session:
        await db.check_pricing_schemes_exists(session, 'Y0')
        await db.check_pricing_schemes_exists(session, 'O0')
        await db.check_pricing_schemes_exists(session, 'W0')

        for market in await get_markets(session):
            data = await utils.build_offers_data(yandex_offers_df[((yandex_offers_df['market'] == market.type) & (yandex_offers_df['name_of_shop'] == market.name))], setup_mode=True, market=market)
            await db.create_offers(session, data)
            backend_logger.info(f'{market.type}({market.name}) offers created: {len(data)}')


async def update_offers(db_session_fabric,
                        api_session_fabric,
                        user_ids: Sequence[int]):
    """ Метод для обновления информации о карточках магазинов """
    backend_logger.info('Start update offers')
    mapping_fields = ['sku', 'name_of_shop', 'market']
    start_time = datetime.now()

    # синхронизируем из карточек в каталог
    reverse_sync_interactor = ReverseSynchronizationInteractor(
        DBMetadataService({'Offer': Offer,
                           'CatalogItem': CatalogItem}),
        db_session_fabric)
    await reverse_sync_interactor(skus=[])
    backend_logger.info('Reverse synchronization completed')

    # синхронизируем из каталога в карточки
    sync_interactor = SynchronizationInteractor(
        DBMetadataService({'Offer': Offer,
                           'CatalogItem': CatalogItem}),
        db_session_fabric)
    await sync_interactor(skus=[])
    backend_logger.info('Synchronization completed')


    async with db_session_fabric() as session:
        # получение информации о маркетах из БД
        markets = await get_markets(session)
        backend_logger.debug(f"Markets: {markets}")

        # Перевычисление значений в карточках и их сохранение в БД
        await recalculate_values(session)

    # Получаем карточек товаров из БД
    db_offers = await get_offers_list(db_session_fabric)
    db_offers_df = pd.DataFrame([offer.model_dump() for offer in db_offers])

    # Получаем товары из апи
    api_interactor = ApiInteractor(api_session_fabric=api_session_fabric,
                                   db_session_fabric=db_session_fabric)

    api_offers = await api_interactor.get_offers_list()
    api_offers_df = pd.DataFrame(api_offers)

    common_columns = (set(db_offers_df.columns.tolist()) & set(api_offers_df.columns.tolist())) - set(mapping_fields)
    merged_offers = pd.merge(db_offers_df, api_offers_df, on=mapping_fields, how='outer', indicator=True, suffixes=(None, '__api'))

    to_update_offers = merged_offers[merged_offers['_merge'] == 'both']
    to_delete_offers = merged_offers[merged_offers['_merge'] == 'left_only']
    to_create_offers = merged_offers[merged_offers['_merge'] == 'right_only']
    del merged_offers
    to_create_offers = (
        to_create_offers
        .drop(columns=common_columns)
        .drop(columns=['_merge', 'id'], errors='ignore')
        .rename(columns={f'{column}__api': column for column in common_columns})[api_offers_df.columns.tolist()]
    )

    discounts = get_seller_discount_from_page(
        to_update_offers[to_update_offers['market'] == 'wildberries']
    )
    update_discounts(discounts, to_update_offers)

    # Создаем переменную с данными для отправки цен в апи
    to_update_price_df = to_update_offers[
        (
            (to_update_offers['auto_price_control'] == True) &
            ((to_update_offers['target_price'] != to_update_offers['current_price__api']) |
             (to_update_offers['seller_discount'] != to_update_offers['seller_discount__api']))
        )
        ][[
            'sku', 'market', 'name_of_shop', 'target_price', 'current_price__api',
            'manual_min_price', 'use_manual_min_price',
            'total_price', 'auto_min_price', 'auto_participation_in_promotions',
            'vendor_code', 'discount_base_price', 'seller_discount', 'seller_discount_changed'
        ]].copy()

    backend_logger.info('Update dataframe length: %s', len(to_update_offers))

    backend_logger.info('Update price dataframe length: %s', len(to_update_price_df))

    # Считаем значения, которые требуют настроек и целевой цены
    for market in markets:
        # пересчет текущей цены до скидки для карточек магазина
        to_update_price_df['discount_base_price'] = np.where(
            (to_update_price_df['market'] == market.type) & (to_update_price_df['name_of_shop'] == market.name),
            to_update_price_df['target_price'] * (1.0 + market.price_before_discount / 100),
            to_update_price_df['discount_base_price']
        )

    # Обновление цен для тех карточек, где включен автоконтроль цен
    await update_offers_price(to_update_price_df,
                              db_session_fabric,
                              api_session_fabric)

    del to_update_price_df


    # Двойная синхронизация полей
    for tracked_column in CONTROL_CHANGES:
        to_update_offers[f'{tracked_column}_changed'] = np.where(
            to_update_offers[tracked_column] != to_update_offers[f'{tracked_column}__api'],
            True,
            False
        )

    # Обновляем атрибуты у тех товаров, в которых были изменения по полям для двойной синхронизации
    to_update_attributes = to_update_offers.query(' | '.join([f'{i}_changed' for i in (*CONTROL_CHANGES, 'seller_discount', 'old_discount')]))
    del to_update_offers

    backend_logger.info(f'Found offers to update attributes: {len(to_update_attributes)}')
    await update_offers_attributes(to_update_attributes, api_session_fabric, db_session_fabric)
    del to_update_attributes
    # Создаем новые товары
    for market in markets:
        to_create_df_chunked = await utils.build_offers_data(to_create_offers[((to_create_offers['market'] == market.type) & (to_create_offers['name_of_shop'] == market.name))], market, setup_mode=True)
        await db.create_offers(session, to_create_df_chunked)
        backend_logger.info(f'New offers for {market.name}({market.type}) created: {len(to_create_df_chunked)}')


    # Создать новые товары в моих остатках
    await create_own_storage_stocks(session)
    backend_logger.info('Own storage stocks created')

    # Обновляем товары из апи для обратной синхронизации
    api_offers = await api_interactor.get_offers_list()
    api_offers_df = pd.DataFrame(api_offers)
    db_offers_small_df = db_offers_df[['id', 'sku', 'market', 'name_of_shop']]
    merged_offers = api_offers_df.merge(db_offers_small_df, on=['sku', 'market', 'name_of_shop'])

    update_api_discounts(discounts, merged_offers)


    for tracked_column in CONTROL_CHANGES:
        api_offers_df[f'{tracked_column}_changed'] = False

    update_api_interactor = UpdateOfferFromApi(DBMetadataService({'Offer': Offer,
                                                                  'CatalogItem': CatalogItem}), get_db_session)
    await update_api_interactor(merged_offers, skus=[], exclude_fields={})

    # Удаляем товары
    backend_logger.info(f"Offers to delete: {len(to_delete_offers)}")

    await delete_offers(to_delete_offers)

    # Пересчитать все
    await recalculate_values(session)
    backend_logger.info('Offers recalculated')

    await update_logs(session, user_ids[0], {'updated_at': datetime.now()})
    await update_logs(session, user_ids[1], {'updated_at': datetime.now()})

    _time = datetime.now() - start_time
    backend_logger.info(f'Offers update completed in {_time}')


async def delete_offers(offers: pd.DataFrame):
    del_offers = [
        OfferDelete(
            sku=offer['sku'],
            name_of_shop=offer['name_of_shop'],
            market=offer['market'],
        )
        for _, offer in offers.iterrows()
    ]

    async with async_session() as session:
        return await db.delete_offers(session, del_offers)


async def update_offers_price(offers: pd.DataFrame | list[OfferOut],
                              db_session_fabric: IDbSessionFabric,
                              api_session_fabric: IApiSessionFabric):
    """ Обновление цен в карточках в магазинах """
    if not config.is_prod:
        backend_logger.info(f'Skip update offers prices app mode is not PROD (current - {config.mode})')
        return

    data = []

    if isinstance(offers, pd.DataFrame):
        data = offers.to_dict('records')
    elif isinstance(offers, list):
        data = [i.model_dump() for i in offers]

    if len(data) == 0:
        backend_logger.info('Skip update prices due to list is empty')
        return

    data = [
        APIPriceChangeData(
            sku=offer_data['sku'],
            market=offer_data['market'],
            name_of_shop=offer_data['name_of_shop'],
            target_price=offer_data['target_price'],
            api_current_price=offer_data['current_price__api'],
            auto_participation_in_promotions=offer_data['auto_participation_in_promotions'],
            auto_min_price=offer_data['target_price'] * offer_data['auto_min_price'] / 100 if all((offer_data['target_price'], offer_data['auto_min_price'])) else None,
            vendor_code=int(offer_data['vendor_code']) if offer_data['vendor_code'] is not None and not np.isnan(
                offer_data['vendor_code']) else None,
            discount_base_price=offer_data['discount_base_price'],
            discount=offer_data['seller_discount'] or 0,
            discount_changed=offer_data['seller_discount_changed'],
        )
        for offer_data in data
    ]

    # изменение цен в магазине
    api_interactor = ApiInteractor(api_session_fabric=api_session_fabric,
                                   db_session_fabric=db_session_fabric)
    await api_interactor.change_prices(data)


async def update_offers_attributes(offers: pd.DataFrame,
                                   api_session_fabric: IApiSessionFabric,
                                   db_session_fabric: IDbSessionFabric):
    data = offers.to_dict('records')

    if not config.is_prod:
        backend_logger.info(f'Skip update offers attributes app mode is not PROD (current - {config.mode})')
        return

    if not len(data):
        backend_logger.info('Skip update offers attributes due to list is empty')
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
            vendor_code=offer_data['vendor_code'],
            self_weight = offer_data['self_weight'],
            self_length = offer_data['self_length'],
            self_width = offer_data['self_width'],
            self_height = offer_data['self_height']
        )
        for offer_data in data if not np.isnan(offer_data['self_width']) and
                                  not np.isnan(offer_data['self_height']) and
                                  not np.isnan(offer_data['self_weight'])
    ]


    api_interactor = ApiInteractor(api_session_fabric=api_session_fabric,
                                   db_session_fabric=db_session_fabric)
    await api_interactor.change_offers(data)


    return data


async def recalculate_values(session: AsyncSession, offers_filter: OffersFilter | None = None):
    """ Метод для обновления вычисляемых значений карточек в БД """
    # Получение карточек
    offers: list[OfferOut] = []
    offer_repository = OfferRepository(session)
    async for offer_chunk in offer_repository.offer_list(query_filter=offers_filter):
        offers += offer_chunk

    df = pd.DataFrame([offer.model_dump() for offer in offers])
    df.drop('dollar_cost_price_updated_at', axis=1, inplace=True, errors='ignore')
    df.fillna(np.nan, inplace=True)
    df.drop('dollar_cost_price_updated_at', axis=1, inplace=True, errors='ignore')

    if df.empty:
        return

    for market in await get_markets(session):
        # выбираем карточки с конкретного магазина и обновляем значения в них
        df1 = await utils.calculate_offers_values(df[((df['name_of_shop'] == market.name) & (df['market'] == market.type))], market)
        df1.replace({np.nan: None}, inplace=True)
        exclude_columns = set(df1.columns.values.tolist()) - set(i.name for i in Offer.__table__.columns)
        df1.drop(columns=exclude_columns, inplace=True)
        # Обновляем карточки в БД
        await db.change_offers(session, offers=df1.to_dict('records'), mapping_fields=['id'])


@error_handler('Ошибка импорта')
async def import_data(data: bytes, market: Market, import_type: ImportType, name_of_shop: str | None, user_id: int, file_extension: str = 'xlsx') -> None:
    async with async_session() as session:
        await get_user_settings(session, user_id)

    match import_type:
        case ImportType.TABLE:
            return await import_offers(data, name_of_shop, market, file_extension)

        case ImportType.SIZES:
            return await import_sizes(data, name_of_shop, market, file_extension)

        case ImportType.PRICES:
            return await import_prices(data, name_of_shop, market, file_extension)

        case _:
            raise NotImplementedError(f'Import type "{import_type}" not implemented yet')


async def import_offers(data, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
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
            backend_logger.error('Error while updating offers in import offers', exc_info=e)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Некоректные данные.')

        await recalculate_values(session, df[['sku', 'name_of_shop', 'market']])


async def import_prices(data, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
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

        await recalculate_values(session)


async def import_sizes(data, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
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
        except Exception:
            backend_logger.error('Error while update price in import sizes', exc_info=True)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Некоректные данные.')

        await recalculate_values(session)


async def export_offers(offers_filter: OffersFilter | None = None) -> str:

    offers = await get_offers_list(get_db_session, offers_filter=offers_filter)
    exclude_columns = set()
    exclude_columns.update(*[f'{i}_changed' for i in CONTROL_CHANGES])

    df = pd.DataFrame([offer.model_dump(exclude=exclude_columns) for offer in offers])
    df['dollar_cost_price_updated_at'] = df['dollar_cost_price_updated_at'].astype('string')
    df['dollar_cost_price_updated_at'].fillna('', inplace=True)
    df['dollar_cost_price_updated_at'] = df['dollar_cost_price_updated_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y') if x else x)
    df.drop(columns=list(exclude_columns), errors='ignore', inplace=True)
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
        await get_user_settings(session, user_id)

        await db.change_pricing_scheme(session, data)
        await recalculate_values(session)


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
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'src/DejaVuSerif.ttf'))

        if len(violators):
            f = [
                Paragraph(f'{i+1}. SKU: {violator.sku}, Маркетплейс: {violator.market}, Магазин: {violator.name_of_shop}, Цена: {round(violator.price)}, РРЦ: {round(violator.recommended_retail_price)}', style=ParagraphStyle('ParStyles', fontName='DejaVuSerif', leading=20))
                for i, violator in enumerate(violators)]
        else:
            f = [Paragraph('Нарушителей не найдено.', style=ParagraphStyle('ParStyles', fontName='DejaVuSerif', leading=20))]
        canvas = SimpleDocTemplate("data/violators.pdf", )
        canvas.build(f)

        return "data/violators.pdf"

async def reset_track_markers() -> None:
    async with async_session() as session:
        await db.reset_all_track_offers_markers(session)
