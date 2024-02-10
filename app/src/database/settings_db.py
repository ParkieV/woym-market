from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import settings_schemas as schema
from src.database.models.models import Logs, Settings, TableInfo
from src.schemas.settings_schemas import TableInfoOut, TableInfoCreate


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


async def create_table(session: AsyncSession, settings_id: int, data: TableInfoCreate) -> TableInfoOut:
    table_db = TableInfo(settings_id=settings_id, **data.model_dump())
    session.add(table_db)
    await session.commit()
    return TableInfoOut.model_validate(table_db, from_attributes=True)


async def get_table(session: AsyncSession, settings_id: int, name: str):
    query = select(TableInfo).where(TableInfo.settings_id==settings_id).where(TableInfo.name==name)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_table(session: AsyncSession, settings_id: int, data: schema.TableInfoUpdate) -> None:
    query = update(TableInfo).where((TableInfo.settings_id == settings_id) & (TableInfo.name == data.name)).values(data.model_dump())
    await session.execute(query)
    await session.commit()


async def delete_table(session: AsyncSession, settings_id: int, names: list[str]) -> None:
    stmp = delete(TableInfo).where(TableInfo.settings_id==settings_id).where(TableInfo.name.in_(names))
    await session.execute(stmp)
    await session.commit()


