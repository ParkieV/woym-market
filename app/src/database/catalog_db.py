from typing import Iterable

import pandas as pd
from sqlalchemy import select, update, func, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.models.models import CatalogItem, Offer
from src.schemas import catalog_schemas as schemas


async def get_all_catalog_items(session: AsyncSession) -> list[CatalogItem]:
    catalog_query = select(CatalogItem).options(selectinload(CatalogItem.synchronization))
    return [schemas.CatalogItem.model_validate(i, from_attributes=True) for i in
            (await session.execute(catalog_query)).scalars()]


async def change_catalog_items(session: AsyncSession, items: list[schemas.CatalogItemUpdate] | pd.DataFrame) -> None:
    for item in items:
        synchronization_info = item.synchronization.copy()
        await set_offers_sync(session, synchronization_info)

        changed_data = item.model_dump(exclude_unset=True)
        if 'synchronization' in changed_data: changed_data.pop('synchronization')

        item_stmp = update(CatalogItem).where(CatalogItem.sku == item.sku).values(**changed_data)
        await session.execute(item_stmp)
        await session.execute(update(CatalogItem).where(CatalogItem.sku == item.sku).values(
            volume=CatalogItem.self_width * CatalogItem.self_length * CatalogItem.self_height / 1000
        ))

    await session.commit()

    # await sync_catalog_items_with_offers(session, skus=[i.sku for i in items])


async def set_offers_sync(session: AsyncSession, items: list[schemas.SynchronizationOffer]):
    for item in items:
        stmp = update(Offer).where(Offer.id == item.id).values(synchronization=item.synchronization)
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


async def sync_catalog_items_with_offers(session: AsyncSession, skus: list[str] | None = None,
                                         exclude_fields: list | None = None):
    detect_changes = ['name', 'description']

    _exclude_fields = {'id', 'sku', 'search_words', 'barcodes'}

    if exclude_fields:
        _exclude_fields.update(set(exclude_fields))

    offer_columns = set(Offer.__table__.columns.keys())
    catalog_columns = set(CatalogItem.__table__.columns.keys())

    common_columns = (offer_columns & catalog_columns) - _exclude_fields

    # Формируем словарь значений для обновления
    update_values = {col: getattr(CatalogItem, col) for col in common_columns}

    # Поисквовые слова изменяются только для озона
    update_search_words = {'search_words': case(
        (Offer.market == 'ozon', CatalogItem.search_words)
        , else_=Offer.search_words)}

    # Штрихкоды изменяются только у яндекса
    update_barcodes = {'barcodes': case(
        (Offer.market == 'yandex', CatalogItem.barcodes)
        , else_=Offer.barcodes)}

    update_values.update(update_barcodes)
    update_values.update(update_search_words)

    # Формируем словарь значений для проверки, что поле было изменено
    detect_changes_values = {
        getattr(Offer, f'{i}_changed'): or_(getattr(Offer, f'{i}_changed'), (
                func.coalesce(getattr(CatalogItem, i), 'unknown') != func.coalesce(getattr(Offer, i), 'unknown')))
        for i in detect_changes
    }

    # Поисковые слова изменяемые только для озона, поэтому тречим изменения только у него
    detect_search_words_changes_for_ozon = {
        'search_words_changed': case(
            (Offer.market == 'ozon', or_(Offer.search_words_changed, (func.coalesce(CatalogItem.search_words, 'unknown') != func.coalesce(Offer.search_words,'unknown')))),
            else_=Offer.search_words_changed)
    }

    # Поисковые слова изменяемые только для озона, поэтому тречим изменения только у него
    detect_barcodes_changes_for_yandex = {
        'barcodes_changed': case(
            (Offer.market == 'yandex', or_(Offer.barcodes, (
                        func.coalesce(CatalogItem.barcodes, 'unknown') != func.coalesce(Offer.barcodes, 'unknown')))),
            else_=Offer.barcodes)
    }

    update_values.update(detect_barcodes_changes_for_yandex)
    update_values.update(detect_changes_values)
    update_values.update(detect_search_words_changes_for_ozon)

    stmp = (
        update(Offer)
        .where(Offer.synchronization == True, Offer.sku == CatalogItem.sku)
        .values(update_values)
        .execution_options(synchronize_session="fetch")
    )

    if skus:
        stmp = stmp.where(Offer.sku.in_(skus))

    await session.execute(stmp)
    await session.commit()


async def set_supplier_available(session: AsyncSession, skus: Iterable[str], value: bool) -> None:
    for sku in skus:
        stmp = update(CatalogItem).where(CatalogItem.sku.endswith(sku)).values(
            supplier_available=value,
            dollar_cost_price_updated_at=func.now(),
        )
        await session.execute(stmp)

    await session.commit()
