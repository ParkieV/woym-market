from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import HTTPException
from starlette import status

from logs import get_logger
from src.database.db import async_session
from src.database import offer_db
from src.database import catalog_db as db
from src.schemas.catalog_schemas import CatalogItemCreate, CatalogItem, CatalogItemUpdate
from src.services.base_utils import parce_field_names, bytes_to_data_frame, parce_sizes_list, parce_purchase_list
from src.services.offer_service import recalculate_values

logger = get_logger(__name__)


async def setup_catalog_items() -> None:
    async with async_session() as session:

        offer_skus = set(await offer_db.get_unique_skus(session))
        item_skus = set(await db.get_unique_skus(session))
        new_skus = offer_skus - item_skus

        new_items = [CatalogItemCreate(sku=sku, catalog_note='Новый товар') for sku in new_skus]
        await db.create_catalog_items(session, new_items)

        if new_items:
            logger.info(f'Catalog items created: {len(new_items)}')
            return

        logger.info('New products not found to create catalog items')


async def get_catalog_items() -> list[CatalogItem]:
    async with async_session() as session:
        return await db.get_all_catalog_items(session)


async def change_catalog_items(items: list[CatalogItemUpdate]) -> None:
    async with async_session() as session:
        await db.change_catalog_items(session, items)
        logger.info(f'Catalog items changed: {len(items)}')

        to_recalculate_offer_ids = [i.id for item in items for i in item.synchronization if i.synchronization]

        if to_recalculate_offer_ids:
            await recalculate_values(session, {'id': i for i in to_recalculate_offer_ids})


async def sync_catalog_items_with_offers(skus: list[str] | None = None, exclude_fields: list | None = None) -> None:
    async with async_session() as session:
        await db.sync_catalog_items_with_offers(session, skus=skus, exclude_fields=exclude_fields)


async def export_catalog_items() -> Path:
    catalog_items = await get_catalog_items()
    df = pd.DataFrame([i.model_dump() for i in catalog_items])
    df.drop(columns=['synchronization'], inplace=True, errors='ignore')
    df.rename(columns=parce_field_names(CatalogItem), inplace=True)

    path = Path('data/catalog_items.xlsx')
    df.to_excel(str(path), index=False)
    return path


async def import_catalog_items(file: bytes, file_extension: str = '.xlsx') -> list[CatalogItem]:
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


async def import_item_sizes(data: bytes, file_extension: str = '.xlsx'):
    df = parce_sizes_list(data, file_extension=file_extension)
    to_update_data = [CatalogItemUpdate(**i) for i in df.to_dict('records')]
    async with async_session() as session:
        await db.change_catalog_items(session, to_update_data)


async def import_item_prices(data: bytes, file_extension: str = '.xlsx'):
    df = parce_purchase_list(data, file_extension=file_extension)
    to_update_data = [CatalogItemUpdate(**i) for i in df.to_dict('records')]
    async with async_session() as session:
        await db.change_catalog_items(session, to_update_data)

        import_skus = set(df['sku'].values.tolist())
        db_skus = set(await db.get_unique_skus(session))

        await db.set_supplier_available(session, db_skus & import_skus, True)
        await db.set_supplier_available(session, db_skus - import_skus, False)

