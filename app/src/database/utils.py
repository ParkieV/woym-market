# TODO проверить как работает с пустым результатом
from typing import Type, Any

from pydantic import BaseModel
from sqlalchemy import ColumnElement, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.base import Base


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
