from src.database import settings_db as db
from src.database.db import async_session
from src.schemas.settings_schemas import SettingsUpdate, TableInfoUpdate, TableInfoCreate, TableInfoOut, \
    MarketUpdate, MarketCreate
from src.services.offer_service import recalculate_values


async def get_logs(user_id: int):
    async with async_session() as session:
        return await db.get_logs_by_user_id(session, user_id)


async def create_logs(user_id: int):
    async with async_session() as session:
        return await db.create_logs(session, user_id)


async def update_logs(user_id: int, data: dict):
    async with async_session() as session:
        return await db.update_logs(session, user_id, data)


async def create_settings(user_id: int):
    async with async_session() as session:
        settings = await db.create_user_settings(session, user_id)
        await db.create_table(session, settings.id, TableInfoCreate(name='offers', data=None))
        return settings


async def get_settings(user_id: int):
    async with async_session() as session:
        return await db.get_user_settings(session, user_id)


async def update_settings(user_id: int, data: SettingsUpdate):
    async with async_session() as session:
        await db.update_user_settings(session, user_id, data)
        settings = await db.get_user_settings(session, user_id)
        await recalculate_values(session, settings)


async def update_table(user_id: int, table_name: str, data: TableInfoUpdate):
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.update_table(session, settings.id, table_name, data)


async def get_table(user_id: int, name: str) -> TableInfoOut:
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.get_table(session, settings.id, name)


async def create_table(data: TableInfoCreate, user_id: int) -> TableInfoOut:
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.create_table(session, settings.id, data)


async def delete_tables(data: list[str], user_id: int):
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.delete_table(session, settings.id, data)


async def get_markets():
    async with async_session() as session:
        return await db.get_markets(session)


async def create_market(data: MarketCreate):
    async with async_session() as session:
        return await db.create_market(session, data)


async def change_market(_id: int, data: MarketUpdate):
    async with async_session() as session:
        await db.change_market(session, _id, data)


async def delete_market(_id: int):
    async with async_session() as session:
        await db.delete_market(session, _id)
