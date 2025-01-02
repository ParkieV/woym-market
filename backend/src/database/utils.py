import asyncio
from typing import Type, Any, Literal

from pydantic import BaseModel
from sqlalchemy import ColumnElement, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from logs import get_logger
from src.database.db import async_session
from src.database.models.base import Base
from src.schemas.catalog_schemas import CatalogItemCreate
from src.shared.exceptions import MappingError
from src.database.offer_db import get_offers_list
from src.database.catalog_db import create_catalog_items
from src.schemas.filters.offers_filter import SKUOnlyOffersFilter


logger = get_logger(__name__)

async def row_to_dict(row) -> dict:
    return dict(row._mapping)


# TODO проверить как работает с пустым результатом
async def row_list_to_dict_list(row_list) -> list[dict]:
    dict_list: list[dict] = []
    for row in row_list:
        dict_list.append(dict(row._mapping))
    return dict_list


async def add_to_list(request) -> list[dict]:
    data = []
    for row in request:
        data.append(row._asdict())
    return data


async def _update_or_create_object(
        session: AsyncSession,
        model: Type[Base],
        data: BaseModel,
        update_by:  ColumnElement[bool],
        model_schema: Type[BaseModel]
) -> (Any, bool):
    query = select(model).where(update_by).distinct()
    result = await session.execute(query)
    object_db = result.scalar_one_or_none()
    created = object_db is None

    if object_db is None:
        object_db = model(**data.model_dump())
        session.add(object_db)
        await session.commit()
    else:
        stmp = (
            update(model)
            .where(update_by)
            .values(**data.model_dump())
        )
        await session.execute(stmp)
        await session.commit()
        query = select(model).filter_by(**data.model_dump())
        object_db = (await session.execute(query)).scalar_one()

    return model_schema.model_validate(object_db, from_attributes=True), created


async def _get_or_create(
        session: AsyncSession,
        model: Type[Base],
        data: BaseModel,
        filter_by:  ColumnElement[bool],
        model_schema: Type[BaseModel]
) -> (Any, bool):
    query = select(model).where(filter_by)
    result = await session.execute(query)
    
    object_db = result.scalar()
    created = object_db is None
    
    if created:
        object_db = model(**data.model_dump())
        session.add(object_db)
        await session.commit()
        await session.refresh(object_db)
        
    return model_schema.model_validate(object_db, from_attributes=True), created


async def duplicate_offers_to_catalog() -> None:
    """ Создает несозданные в каталоге записи карточек товарах """
    offer_filter = SKUOnlyOffersFilter()

    async with async_session() as session:
        async for offers in get_offers_list(session, chunk_size=1000, offers_filter=offer_filter):
            print("chunks size:", len(offers))
            print("first chunk:", offers[0].model_dump())
            sku_set = set([offers.sku for offers in offers])
            offers_dto = [CatalogItemCreate(
                            sku=sku,
                            use_promotion_price=False,
                            supplier_available=False,
                            search_words_changed=False) for sku in sku_set]
            await create_catalog_items(session, offers_dto)
        logger.debug('Create catalog successfully!')


def mapping_pydantic_to_sqlalchemy_dict(
        pydantic_model: BaseModel,
        sqlalc_model: type[DeclarativeBase],
        *,
        extra: Literal['allow'] | None = None) -> dict[str, Any]:
    """
    Mapping Pydantic model to dict according to SQLAlchemy model structure.
    :param pydantic_model: Pydantic model.
    :param sqlalc_model: SQLAlchemy model for validating.
    :param extra: Parameter to check if Pydantic model has extra attributes for SQLAlchemy model.
    :return: Validating with SQLAlchemy model dictionary.
    """
    data = pydantic_model.model_dump()
    sqlalchemy_mapper = sqlalc_model.__mapper__
    if extra == 'allow':
        return {k: v for k, v in data.items() if k in sqlalchemy_mapper.columns}
    else:
        try:
            return {k: v for k, v in data.items() if sqlalchemy_mapper.columns[k]}
        except KeyError as key_err:
            MappingError(f"Не удалось представить объект {pydantic_model.__class__.__name__} в виде словаря: {sqlalc_model.__class__.__name__} не содержит атрибут '{key_err.args[0]}'")


if __name__ == '__main__':
    logger.info('Duplicate started!')
    asyncio.run(duplicate_offers_to_catalog())
    logger.info('Duplicate finished!')
