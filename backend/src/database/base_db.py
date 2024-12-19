from select import select
from typing import Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.base import Base
from src.schemas.filters.filter_schemas import PagingFilter


async def create_all(session: AsyncSession, items: list[BaseModel], db_model: Type[Base],  **extra):
    new_db_items = [db_model(**item.model_dump(), **extra) for item in items]
    session.add_all(new_db_items)
    await session.commit()


async def create_one(session: AsyncSession, item: BaseModel, db_model: Type[Base], model_schema: Type[BaseModel] | None = None, **extra) -> BaseModel | Base:
    new_item = db_model(**item.model_dump(), **extra)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)

    if model_schema:
        return model_schema.model_validate(new_item, from_attributes=True)

    return new_item


async def get_scalars_all(session: AsyncSession, db_model: Type[Base],  schema: Type[BaseModel], paging: PagingFilter | None = None):
    query = select(db_model)

    if paging:
        query = paging(query)

    result = await session.execute(query)