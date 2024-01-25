from src.database import settings_db as db
from src.database.db import async_session
from src.schemas.offer_schemas import OfferOut
from src.schemas.settings_schemas import SettingsUpdate, ColumnUpdate


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
        await db.create_columns(session, settings, OfferOut.columns_info(['group_sellers_amount', 'business_id']))
        return settings


async def get_settings(user_id: int):
    async with async_session() as session:
        return await db.get_user_settings(session, user_id)


async def update_settings(user_id: int, data: SettingsUpdate):
    async with async_session() as session:
        return await db.update_user_settings(session, user_id, data)


async def update_columns(user_id: int, data: list[ColumnUpdate]):
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.update_columns(session, settings.id, data)

