from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.models.models import CatalogItem, Offer
from src.schemas import catalog_schemas as schemas


async def get_all_catalog_items(session: AsyncSession) -> list[CatalogItem]:
    catalog_query = select(CatalogItem).options(selectinload(CatalogItem.synchronization))
    return [schemas.CatalogItem.model_validate(i, from_attributes=True) for i in (await session.execute(catalog_query)).scalars()]


async def change_catalog_items(session: AsyncSession, items: list[schemas.CatalogItemUpdate]) -> None:
    for item in items:
        synchronization_info = item.synchronization.copy()
        await synchronize_offers(session, synchronization_info)

        changed_data = item.model_dump()
        changed_data.pop('synchronization')

        item_stmp = update(CatalogItem).where(CatalogItem.sku == item.sku).values(**changed_data)
        await session.execute(item_stmp)

    await session.commit()


async def synchronize_offers(session: AsyncSession, items: list[schemas.SynchronizationOffer]):
    for item in items:
        stmp = update(Offer).where(Offer.sku == item.sku).values(synchronization=item.synchronization)
        await session.execute(stmp)

    await session.commit()


async def create_catalog_items(session: AsyncSession, items: list[schemas.CatalogItemCreate]):
    new_items = [CatalogItem(**item.model_dump(exclude_unset=True)) for item in items]
    session.add_all(new_items)
    await session.commit()


async def get_unique_skus(session: AsyncSession) -> list[str]:
    query = select(CatalogItem.sku).distinct()
    result = await session.execute(query)
    return [i[0] for i in result.all()]


async def sync_catalog_items_with_offers(session: AsyncSession, exclude_fields: list | None = None):
    _exclude_fields = {'id', 'sku'}

    if exclude_fields:
        _exclude_fields.add(exclude_fields)

    offer_columns = set(Offer.__table__.columns.keys())
    catalog_columns = set(CatalogItem.__table__.columns.keys())

    common_columns = (offer_columns & catalog_columns) - _exclude_fields

    # Формируем словарь значений для обновления
    update_values = {col: getattr(CatalogItem, col) for col in common_columns}

    stmp = (
        update(Offer)
        .where(Offer.synchronization == True, Offer.sku == CatalogItem.sku)
        .values(update_values)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmp)
    await session.commit()

