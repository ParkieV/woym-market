from src.database.db import async_session
from src.database import offer_db
from src.database import catalog_db as db
from src.schemas.catalog_schemas import CatalogItemCreate


async def setup_catalog_items() -> None:
    async with async_session() as session:
        offer_skus = set(await offer_db.get_unique_skus(session))
        item_skus = set(await db.get_unique_skus(session))
        new_skus = offer_skus - item_skus

        new_items = [CatalogItemCreate(sku=sku, note='Новый товар') for sku in new_skus]
        await db.create_catalog_items(session, new_items)


async def get_catalog_items():
    async with async_session() as session:
        return await db.get_all_catalog_items(session)
