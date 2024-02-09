import json

from src.database import settings_db as db
from src.database.db import async_session
from src.schemas.settings_schemas import SettingsUpdate, ColumnUpdate, Tables, ColumnCreate, ColumnOut
from src.schemas.offer_schemas import OfferOut


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
        await db.create_columns(session, settings, [ColumnCreate(table=Tables.OFFERS, data=None) for _ in OfferOut.fields().keys()])
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


async def get_columns(user_id: int, table: Tables) -> list[ColumnOut]:
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.get_columns(session, settings.id, table)


async def create_columns(data: list[ColumnCreate], user_id: int) -> list[ColumnOut]:
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.create_columns(session, settings.id, data)


async def delete_columns(data: list[int], user_id: int):
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.delete_columns(session, settings.id, data)
