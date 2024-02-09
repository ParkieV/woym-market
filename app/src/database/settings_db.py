from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import settings_schemas as schema
from src.database.models.models import Logs, Settings, ColumnInfo
from src.schemas.settings_schemas import ColumnOut, ColumnCreate


async def create_logs(session: AsyncSession, user_id: int) -> Logs:
    logs_db = Logs(user_id=user_id)
    session.add(logs_db)
    await session.commit()
    await session.refresh(logs_db)
    return logs_db


async def get_logs_by_user_id(session: AsyncSession, user_id: int) -> Logs | None:
    query = select(Logs).where(Logs.user_id == user_id)
    rez = await session.execute(query)
    return rez.scalar_one_or_none()


async def update_logs(session: AsyncSession, user_id: int, data: dict):
    query = update(Logs).where(Logs.user_id == user_id).values(**data)
    await session.execute(query)
    await session.commit()


async def create_user_settings(session: AsyncSession, user_id: int) -> Settings:
    settings_db = Settings(user_id=user_id)
    session.add(settings_db)
    await session.commit()
    await session.refresh(settings_db)
    return settings_db


async def get_user_settings(session: AsyncSession, user_id: int) -> Settings | None:
    query = select(Settings).where(Settings.user_id == user_id)
    res = await session.execute(query)
    return res.scalar_one_or_none()


async def update_user_settings(session: AsyncSession, user_id: int, settings_update: schema.SettingsUpdate):
    query = update(Settings).where(Settings.user_id == user_id).values(**dict(settings_update))
    await session.execute(query)
    await session.commit()


async def create_columns(session: AsyncSession, settings_id: int,  data: list[ColumnCreate]) -> list[ColumnOut]:
    columns_db = [ColumnInfo(settings_id=settings_id, **dict(column)) for column in data]
    session.add_all(columns_db)
    await session.commit()
    return [ColumnOut.model_validate(column, from_attributes=True) for column in columns_db]


async def get_columns(session: AsyncSession, settings_id: int, table: schema.Tables) -> list[ColumnOut]:
    query = select(ColumnInfo).where(ColumnInfo.settings_id==settings_id).where(ColumnInfo.table==table)
    result = await session.execute(query)
    return [schema.ColumnOut.model_validate(i, from_attributes=True) for i in result.scalars().all()]


async def update_columns(session: AsyncSession, settings_id: int,  data: list[schema.ColumnUpdate]) -> None:
    for column in data:
        query = update(ColumnInfo).where((ColumnInfo.settings_id == settings_id) & (ColumnInfo.id == column.id)).values(**dict(column))
        await session.execute(query)

    await session.commit()


async def delete_columns(session: AsyncSession, settings_id: int, ids: list[int]) -> None:
    stmp = delete(ColumnInfo).where(ColumnInfo.settings_id==settings_id).where(ColumnInfo.id.in_(ids))
    await session.execute(stmp)
    await session.commit()


