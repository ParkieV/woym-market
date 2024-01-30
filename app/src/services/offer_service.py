from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import async_session
from src.database import offer_db as db
import src.services.offer_utils as utils
from src.schemas.offer_schemas import OfferChange, OfferOut, OfferDelete, ExportType, ImportType, Market
import pandas as pd
from src.api.factory import RepositoryFactory, MPTypes
import numpy as np
from src.services.settings_service import get_settings, update_logs

yandex_repository = RepositoryFactory.get(MPTypes.YANDEX)


async def get_offers(filters: dict[str, Any] | None = None) -> list[OfferOut]:
    async with async_session() as session:
        return await db.get_offers(session, filters)


async def change_offers(offers_data: list[OfferChange], user_id: int):
    if not offers_data:
        return offers_data

    settings = await get_settings(user_id)

    async with async_session() as session:
        offers = await db.get_offers_by_sku_and_shop_name(session, [(i.sku, i.name_of_shop,) for i in offers_data])

        offers_df = pd.DataFrame([offer.model_dump() for offer in offers])
        changes = pd.DataFrame([offer.model_dump() for offer in offers_data])

        changed_offers = utils.update_offers_data(offers_df, changes, settings)
        await db.update_offers(session, changed_offers, mapping_columns=['name_of_shop'])
        return await db.get_offers_by_sku_and_shop_name(session, [(i.sku, i.name_of_shop,) for i in offers_data])


async def setup_offers_data(user_id: int):
    settings = await get_settings(user_id)
    yandex_offers = await yandex_repository.get_offers()
    yandex_offers_df = pd.DataFrame(yandex_offers)
    data = utils.build_offers_data(yandex_offers_df, setup_mode=True, settings=settings)

    async with async_session() as session:
        offers_db = await db.create_offers(session, data)
        return offers_db


async def update_offers(user_id: int):
    settings = await get_settings(user_id)

    mapping_fields = ['sku', 'name_of_shop', 'market']

    yandex_offers = await yandex_repository.get_offers()
    db_offers = await get_offers()

    offers_df = pd.DataFrame([offer.model_dump() for offer in db_offers])
    yandex_offers_df = pd.DataFrame(yandex_offers)

    offers_db_identifiers = set([tuple(i.values()) for i in offers_df[mapping_fields].to_dict('records')])
    yandex_offers_identifiers = set([tuple(i.values()) for i in yandex_offers_df[mapping_fields].to_dict('records')])

    to_update = offers_db_identifiers & yandex_offers_identifiers
    to_create = yandex_offers_identifiers - offers_db_identifiers
    to_delete = offers_db_identifiers - yandex_offers_identifiers

    to_update_df = pd.merge(yandex_offers_df, pd.DataFrame(to_update, columns=mapping_fields), how='inner')
    to_create_df = pd.merge(yandex_offers_df, pd.DataFrame(to_create, columns=mapping_fields), how='inner')
    to_create_df = utils.build_offers_data(to_create_df, settings, setup_mode=True)
    to_delete_df = pd.DataFrame(to_delete, columns=mapping_fields)

    async with async_session() as session:
        await db.create_offers(session, to_create_df)
        await db.update_offers(session, to_update_df, mapping_columns=['name_of_shop', 'market'])
        await db.delete_offers(session, to_delete_df)
        await recalculate_values(session, settings)
        await update_yandex_offers_price(session)
        await recalculate_values(session, settings)

    await update_logs(user_id, {'updated_at': datetime.now()})


async def delete_offers(offers: list[OfferDelete]):
    async with async_session() as session:
        return await db.delete_offers(session, [offer.model_dump() for offer in offers])


async def update_yandex_offers_price(session: AsyncSession):
    offers_db = await db.get_offers(session)
    offers_df = pd.DataFrame([offer.model_dump() for offer in offers_db])
    data = offers_df.to_dict('records')
    await yandex_repository.change_prices(data)
    await db.update_offers(session, data, mapping_columns=['name_of_shop'])


async def recalculate_values(session: AsyncSession, settings):
    offers = await get_offers()
    df = pd.DataFrame([offer.model_dump() for offer in offers])
    df = utils.calculate_offers_values(df, settings)
    df.drop('id', axis=1, inplace=True, errors='ignore')

    await db.update_offers(session, df, mapping_columns=['sku', 'name_of_shop'])


async def import_data(data: bytes, market: Market, import_type: ImportType, name_of_shop: str | None, user_id: int, file_extension: str = 'xlsx') -> None:
    settings = await get_settings(user_id)

    if market == Market.ALL:
        market = None

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
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df.fillna({
        'note_1': '',
        'note_2': '',
        'note_3': '',
    }, inplace=True)

    if name_of_shop:
        df = df[df['name_of_shop'] == name_of_shop]

    if market:
        df = df[df['market'] == market]

    db_offers = await get_offers()
    offers_df = pd.DataFrame([offer.model_dump() for offer in db_offers])

    columns_to_change = list(set(df.columns) & set(offers_df.columns))
    df = df[columns_to_change]
    df = df[df['sku'].isin(offers_df['sku'])]
    offers_df = offers_df[offers_df['sku'].isin(df['sku'])]

    changes = utils.update_offers_data(offers_df, df, settings)

    async with async_session() as session:
        await db.update_offers(session, changes, mapping_columns=['name_of_shop', 'market'], endswith_sku=False)


async def import_prices(data, settings, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.drop(df.columns[[3, 4, 6, 7]], axis=1, inplace=True, errors='ignore')
    df.drop([i for i in range(8)], axis=0, inplace=True, errors='ignore')
    df.columns = ['sku', 'name', 'discount_price', 'price']
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    df['dollar_cost_price'] = np.where(
        np.isnan(df['discount_price']),
        df['price'] * (1 - settings.discount_purchase / 100),
        df['discount_price']
    )
    df.drop(['name', 'discount_price', 'price'], axis=1, inplace=True)

    mapping_columns = []

    if name_of_shop:
        df['name_of_shop'] = name_of_shop
        mapping_columns.append('name_of_shop')

    if market:
        df['market'] = market
        mapping_columns.append('market')

    async with async_session() as session:
        await db.update_offers(session, df, mapping_columns=mapping_columns, endswith_sku=True)
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
        await db.update_offers(session, df, mapping_columns=mapping_columns, endswith_sku=True)
        await recalculate_values(session, settings)


async def export_data(market: Market, export_type: ExportType, name_of_shop: str | None):
    if market == Market.ALL:
        market = None

    match export_type:
        case ExportType.TABLE:
            return await export_offers(name_of_shop, market)

        case _:
            raise NotImplemented(f'Export type "{export_type}" not implemented yet')


async def export_offers(name_of_shop: str | None = None, market: str | None = None) -> str:
    filters = {}

    if name_of_shop:
        filters['name_of_shop'] = name_of_shop

    if market:
        filters['market'] = market

    offers = await get_offers(filters)

    df = pd.DataFrame([offer.model_dump() for offer in offers], columns=OfferOut.fields().keys())
    df.drop(['id', 'business_id', 'group_sellers_amount'], axis=1, inplace=True, errors='ignore')

    df.rename(columns=OfferOut.fields(), inplace=True)
    df.to_excel('data/out.xlsx', index=False)
    return 'data/out.xlsx'


