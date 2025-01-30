from src.database import settings_db as db
from src.database.db import async_session
from src.database.models.models import Market
from src.database.utils import mapping_pydantic_to_sqlalchemy_dict
from src.schemas.filters.offers_filter import OffersFilter
from src.schemas.settings_schemas import SettingsUpdate, TableInfoUpdate, TableInfoCreate, TableInfoOut, \
    MarketUpdate, MarketCreate, MarketFullUpdate
from src.services.base_utils import error_handler
from src.services.offer_service import recalculate_values
from src.api.factory import ApiFactory


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
        await db.update_or_create_table(session, TableInfoCreate(name='offers', data=None))
        return settings


async def get_settings(user_id: int):
    async with async_session() as session:
        return await db.get_user_settings(session, user_id)


@error_handler('Не удалось обновить настройки.')
async def update_settings(user_id: int, data: SettingsUpdate):
    async with async_session() as session:
        await db.update_user_settings(session, user_id, data)
        await db.get_user_settings(session, user_id)
        await recalculate_values(session)


async def update_or_create_table(data: TableInfoUpdate):
    async with async_session() as session:
        return await db.update_or_create_table(session, data)


async def get_table(name: str) -> TableInfoOut:
    async with async_session() as session:
        return await db.get_table(session, name)


async def update_table(user_id: int, table_name: str, data: TableInfoUpdate):
    async with async_session() as session:
        await db.get_user_settings(session, user_id)

        return await db.update_table(session, table_name, data)


async def create_table(data: TableInfoCreate) -> TableInfoOut:
    async with async_session() as session:

        return await db.create_table(session, data)


async def delete_tables(data: list[str], user_id: int):
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.delete_table(session, settings.id, data)


async def get_markets():
    async with async_session() as session:
        return await db.get_markets(session)


async def create_market(data: MarketCreate, api_factory: ApiFactory) -> MarketFullUpdate:
    async with async_session() as session:
        api_factory(data.type, session=session, token=data.token, entity_id=data.entity_id, shop_name=data.name)
        return await db.create_market(session, data)


async def change_market(_id: int, data: MarketUpdate | MarketFullUpdate, user_id: int):
    async with async_session() as session:
        market = await db.change_market(session, _id, mapping_pydantic_to_sqlalchemy_dict(data, Market, extra='allow'))
        await recalculate_values(session, offers_filter=OffersFilter(market=market.type, name_of_shop=market.name))


async def delete_market(_id: int):
    async with async_session() as session:
        await db.delete_market(session, _id)
