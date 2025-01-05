from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import HTTPException
from starlette import status

from logs import get_logger
from src.database.catalog import CatalogRepository
from src.database.db import async_session, ISessionFabric
from src.database import catalog as db
from src.database.offer import OfferRepository
from src.schemas.catalog_schemas import CatalogItemCreate, PydanticCatalogItem, CatalogItemUpdate
from src.schemas.offer_schemas import OfferOut
from src.services.base_utils import parce_field_names, bytes_to_data_frame, parce_purchase_list

logger = get_logger(__name__)


async def setup_catalog_items(session_fabric: ISessionFabric) -> None:
    offer_repository = OfferRepository()
    async with session_fabric as session:
        offer_repository.session = session
        db_offers: list[OfferOut] = []
        async for offer_chunk in offer_repository.list():
            db_offers += offer_chunk

        db_offers_df = pd.DataFrame([i.model_dump() for i in db_offers])
        db_offers_skus = set(db_offers_df['sku'].values.tolist())

        catalog_items_skus = set(await db.get_unique_skus(session))

        to_create_skus = db_offers_skus - catalog_items_skus

        if not to_create_skus:
            logger.info(f'New catalog items not found')
            return

        to_create_items_with_cdv = db_offers_df[
            (db_offers_df['sku'].isin(to_create_skus)) &
            (db_offers_df['market'] == 'ozon') &
            (db_offers_df['name_of_shop'] == 'SkrabPlus')
            ].drop_duplicates(subset='sku')

        to_create_items_with_rdv = db_offers_df[(db_offers_df['sku'].isin(to_create_skus)) & (~db_offers_df['sku'].isin(to_create_items_with_cdv['sku']))].drop_duplicates(subset='sku')

        new_items_df = pd.concat([to_create_items_with_cdv, to_create_items_with_rdv])
        new_items_df['dollar_cost_price_updated_at'] = None
        new_items_df.drop(columns=['synchronization'], inplace=True)
        new_items_df['catalog_note'] = 'Новый товары'
        new_items_df = new_items_df.replace({
            np.nan: None
        })
        new_items = [CatalogItemCreate(**i) for i in new_items_df.to_dict(orient='records')]

        if len(new_items) != len(to_create_skus):
            logger.warning(f'Len of new skus and creating skus not equal: {len(new_items)} / {len(to_create_skus)}')

        await db.create_catalog_items(session, new_items)

        logger.info(f'Catalog items created: {len(new_items)}')


async def get_catalog_items(session_fabric: ISessionFabric) -> list[PydanticCatalogItem]:
    catalog_repo = CatalogRepository()
    res = []

    async with session_fabric as session:
        catalog_repo.session = session
        async for chunk in catalog_repo.list():
            res += chunk

    return res


async def change_catalog_items(session_factory: ISessionFabric, items: list[CatalogItemUpdate]) -> None:
    async with session_factory as session:
        await db.change_catalog_items(session, items)


async def sync_catalog_items_with_offers(skus: list[str] | None = None, exclude_fields: list | None = None) -> None:
    async with async_session() as session:
        await db.sync_catalog_items_with_offers(session, skus=skus, exclude_fields=exclude_fields)


async def export_catalog_items() -> Path:
    catalog_items = await get_catalog_items()
    df = pd.DataFrame([i.model_dump() for i in catalog_items])
    df.drop(columns=['synchronization'], inplace=True, errors='ignore')
    df.rename(columns=parce_field_names(PydanticCatalogItem), inplace=True)

    path = Path('data/catalog_items.xlsx')
    df.to_excel(str(path), index=False)
    return path


async def import_catalog_items(file: bytes, file_extension: str = '.xlsx') -> None:
    df = bytes_to_data_frame(file, file_extension=file_extension)
    if 'sku' not in df.columns.values.tolist():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'В файле должна быть колонка "sku"')

    df['sku'] = df['sku'].astype('string')

    columns = parce_field_names(CatalogItemUpdate, reverse=True)

    df = df[list(set(df.columns.values.tolist()) & set(columns.keys()))]
    df.rename(columns=columns, inplace=True)
    df.replace({np.nan: None}, inplace=True)

    to_update_items = [CatalogItemUpdate(**i) for i in df.to_dict('records')]

    await change_catalog_items(to_update_items)


async def import_item_prices(data: bytes, file_extension: str = '.xlsx'):
    df = parce_purchase_list(data, file_extension=file_extension)
    logger.debug('Parsed dataframe')
    to_update_data = [CatalogItemUpdate(**i) for i in df.to_dict('records')]
    async with async_session() as session:
        logger.debug('Start')
        await db.change_catalog_items(session, to_update_data)
        logger.debug('Changed catalog items successfully')
        await db.set_supplier_available(session, [i.sku for i in to_update_data])
        logger.debug('Changed catalog items successfully')


async def reset_track_markers() -> None:
    async with async_session() as session:
        await db.reset_all_track_catalog_markers(session)
