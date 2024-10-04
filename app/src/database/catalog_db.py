from typing import Iterable

import pandas as pd
from sqlalchemy import select, update, func, or_, case, cast, String, and_
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

        track_changes = {
            f'{column}_changed': or_(
                getattr(CatalogItem, f'{column}_changed'),
                func.concat(getattr(CatalogItem, column), '') != str((changed_data[column] or ''))
            )
            for column in CatalogItem.__table__.columns.keys() if column in changed_data and getattr(CatalogItem, column, None) and getattr(CatalogItem, f'{column}_changed', None)
        }

        changed_data.update(track_changes)

        item_stmp = update(CatalogItem).where(CatalogItem.sku == item.sku).values(**changed_data)
        await session.execute(item_stmp)

    await session.commit()


async def set_offers_sync(session: AsyncSession, items: list[schemas.SynchronizationOffer]):
    for item in items:
        stmp = update(Offer).where(Offer.id == item.id).values(
            synchronization=item.synchronization
        )
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


async def sync_catalog_items_with_offers(session: AsyncSession, skus: list[str] | None = None, exclude_fields: list | None = None):
    _exclude_fields = {'id', 'sku'}
    if exclude_fields:
        _exclude_fields.update(exclude_fields)

    offer_columns = set(Offer.__table__.columns.keys())
    catalog_columns = set(CatalogItem.__table__.columns.keys())
    common_columns = (offer_columns & catalog_columns) - _exclude_fields

    # Формируем словарь значений для обновления
    update_values = {col: func.coalesce(getattr(CatalogItem, col), getattr(Offer, col)) for col in common_columns}

    # Поисквовые слова изменяются только для озона
    update_search_words = {'search_words': case(
        (Offer.market == 'ozon', func.coalesce(CatalogItem.search_words, Offer.search_words))
        , else_=Offer.search_words)}

    # Штрихкоды изменяются только у яндекса
    update_barcodes = {'barcodes': case(
        (Offer.market == 'yandex', func.coalesce(CatalogItem.barcodes, Offer.barcodes))
        , else_=Offer.barcodes)}

    update_values.update(update_barcodes)
    update_values.update(update_search_words)

    # Формируем словарь значений для проверки, что поле было изменено
    detect_changes_values = {
        getattr(Offer, f'{col}_changed'): or_(
            getattr(Offer, f'{col}_changed'),
            func.concat(getattr(Offer, col), '') != func.concat(func.coalesce(getattr(CatalogItem, col), getattr(Offer, col)), '')
        )
        for col in common_columns if all((getattr(Offer, f'{col}_changed', None), getattr(CatalogItem, col, None), getattr(Offer, col, None)))
    }

    # Поисковые слова изменяемые только для озона, поэтому тречим изменения только у него
    detect_search_words_changes_for_ozon = {
        'search_words_changed': case(
            (Offer.market == 'ozon', or_(
                Offer.search_words_changed,
                func.concat(Offer.search_words, '') != func.concat(
                    func.coalesce(CatalogItem.search_words, Offer.search_words), '')
            )),
            else_=Offer.search_words_changed)
    }

    # # Штрихкоды изменяемые только для яндекса, поэтому тречим изменения только у него
    detect_barcodes_changes_for_yandex = {
        'barcodes_changed': case(
            (Offer.market == 'yandex', or_(
                Offer.barcodes_changed,
                func.concat(Offer.barcodes, '') != func.concat(func.coalesce(CatalogItem.barcodes, Offer.barcodes), '')

            )),
            else_=Offer.barcodes_changed)
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


async def set_supplier_available(session: AsyncSession, skus: Iterable[str]) -> None:
    for sku in skus:
        available_stmp = (
            update(CatalogItem)
            .where(CatalogItem.sku.in_(sku)).values(
                supplier_available=True,
                dollar_cost_price_updated_at=func.now(),
            )
        )
        await session.execute(available_stmp)

        unavailable_stmp = (
            update(CatalogItem)
            .where(CatalogItem.sku.notin_(sku)).values(
                supplier_available=False,
            )
        )
        await session.execute(unavailable_stmp)

    await session.commit()


async def reverse_sync_offers_with_catalog_items(session: AsyncSession, skus: list[str] | None = None, exclude_fields: list | None = None) -> None:
    _exclude_fields = {'id', 'sku'}
    if exclude_fields:
        _exclude_fields.update(exclude_fields)

    offer_columns = set(Offer.__table__.columns.keys())
    catalog_columns = set(CatalogItem.__table__.columns.keys())
    common_columns = (offer_columns & catalog_columns) - _exclude_fields

    # Формируем словарь значений для обновления
    update_values = {
        col: case(
            (getattr(CatalogItem, f'{col}_changed') == False, func.coalesce(getattr(Offer, col), getattr(CatalogItem, col))),
            else_=getattr(CatalogItem, col)
        )
        for col in common_columns if getattr(CatalogItem, f'{col}_changed', None)
    }

    track_changes = {
        f'{col}_changed': or_(
            getattr(CatalogItem, f'{col}_changed'),
            func.concat(getattr(CatalogItem, col), '') != func.concat(func.coalesce(getattr(Offer, col), getattr(CatalogItem, col)), '')
        )
        for col in common_columns if all((getattr(CatalogItem, f'{col}_changed', None), getattr(CatalogItem, col, None), getattr(Offer, col, None)))
    }

    update_values.update(track_changes)

    stmp = (
        update(CatalogItem)
        .where(Offer.id == CatalogItem.reverse_sync_offer_id)
        .values(update_values)
        .execution_options(synchronize_session="fetch")
    )
    if skus:
        stmp = stmp.where(CatalogItem.sku.in_(skus))

    await session.execute(stmp)
    await session.commit()


async def reset_all_track_catalog_markers(session: AsyncSession):
    stmp = update(CatalogItem).values(
        self_weight_changed=False,
        self_length_changed=False,
        self_width_changed=False,
        self_height_changed=False,
        use_promotion_price_changed=False,
        wholesale_dollar_cost_price_changed=False,
        supplier_available_changed=False,
        description_changed=False,
        search_words_changed=False,
        name_changed=False,
        barcodes_changed=False,
    )

    await session.execute(stmp)
    await session.commit()
