from typing import Iterable, AsyncGenerator, TypeVar, Sequence

import pandas as pd
from pydantic import BaseModel
from sqlalchemy import select, update, func, or_, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.interfaces import ICatalogRepository
from src.database.models.models import CatalogItem, Offer
from src.schemas import catalog_schemas as schemas
from src.schemas.catalog_schemas import PydanticCatalogItem
from src.schemas.filters.db_catalog import OfferDataFilter, SkuInArrayFilter, ReverseSyncUpdatingColumnFilter
from src.schemas.filters.interface import IBaseFilter


PydanticModel = TypeVar("PydanticModel", bound=BaseModel)

class CatalogRepository(ICatalogRepository[PydanticModel]):

    @property
    def session(self):
        if self._session is None:
            raise ValueError('Session is not initialized')
        return self._session

    @session.setter
    def session(self, session: AsyncSession):
        self._session = session

    def __init__(self, session: AsyncSession | None = None):
        self._session = session

    async def get(self,
                  identification: str) -> PydanticModel:
        ...

    async def list(self,
                   chunk_size: int | None = None,
                   query_filter: IBaseFilter | None = None) -> AsyncGenerator[list[PydanticModel], None]:
        """
        Return list of catalog items using chunks
        :param chunk_size: size of chunk
        :param query_filter: filters for selecting offers
        :return: Batch of offers
        """
        query = select(CatalogItem).options(selectinload(CatalogItem.synchronization))

        if query_filter is not None:
            query = query_filter(query)

        offset = 0
        while True:
            query = query.limit(chunk_size).offset(offset)
            chunk = (await self.session.execute(query)).scalars().all()
            res = [PydanticCatalogItem.model_validate(item, from_attributes=True) for item in chunk]

            if len(res) == 0:
                return

            yield res

            if chunk_size is None:
                return
            offset += chunk_size

    async def create(self, data: PydanticModel) -> None:
        ...

    async def create_many(self,
                    data: Sequence[PydanticModel]) -> None:
        ...

    async def update(self,
                     identification: str,
                     data: PydanticModel) -> None:
        ...

    async def update_many(self,
                          data: Sequence[PydanticModel],
                          query_filter: IBaseFilter | None = None) -> None:
        ...

    async def synchronization_catalog_from_offer(self,
                 updating_columns: Iterable[str],
                 skus: Sequence[str] | None = None) -> None:
        offer_data_filter = OfferDataFilter()
        sku_in_array_filter = SkuInArrayFilter('catalog_items')
        updating_columns_filter = ReverseSyncUpdatingColumnFilter(updating_columns)

        query = "UPDATE catalog_items\n\tSET "

        query = updating_columns_filter(query)

        query = offer_data_filter(query[:-3]+'\n')

        if skus and len(skus) > 0:
            sku_in_array_filter.skus = skus
            query = sku_in_array_filter(query)

        query = text(query)
        await self.session.execute(query)

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

    await session.flush()


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
    """ Метод для синхронизации данных в карточках и каталоге """
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
    """ Метод для определения наличия товара по sku у поставщиков """
    available_stmt = (
        update(CatalogItem)
        .where(CatalogItem.sku.in_(skus))
        .values(
            supplier_available=True,
            dollar_cost_price_updated_at=func.now(),
        )
    )

    unavailable_stmt = (
        update(CatalogItem)
        .where(~CatalogItem.sku.in_(skus))
        .values(
            supplier_available=False,
        )
    )

    await session.execute(available_stmt)
    await session.execute(unavailable_stmt)

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
