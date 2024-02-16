from typing import Type

from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import settings_schemas as schema
from src.database.models.models import Logs, Settings, TableInfo, Market
from src.schemas.settings_schemas import TableInfoOut, TableInfoCreate, MarketCreate, MarketOut, MarketUpdate, \
    MarketFullUpdate, MarketFullOut, TableInfoUpdate
from .utils import _update_or_create_object


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


async def update_or_create_table(session: AsyncSession, data: TableInfoCreate | TableInfoUpdate) -> TableInfoOut:
    return await _update_or_create_object(
        session,
        TableInfo,
        data,
        TableInfo.name==data.name,
        TableInfoOut
    )


async def get_table(session: AsyncSession, name: str):
    query = select(TableInfo).where(TableInfo.name==name)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def delete_table(session: AsyncSession, settings_id: int, names: list[str]) -> None:
    stmp = delete(TableInfo).where(TableInfo.settings_id==settings_id).where(TableInfo.name.in_(names))
    await session.execute(stmp)
    await session.commit()


async def create_market(session: AsyncSession, data: MarketCreate, model_schema: Type[BaseModel] = MarketOut) -> BaseModel:
    market_db = Market(**data.model_dump())
    session.add(market_db)
    await session.commit()
    return model_schema.model_validate(market_db, from_attributes=True)


async def get_markets(session: AsyncSession, model_schema: Type[BaseModel] = MarketOut) -> list[BaseModel]:
    query = select(Market)
    result = await session.execute(query)
    return [model_schema.model_validate(market, from_attributes=True) for market in result.scalars().all()]


async def change_market(session: AsyncSession, _id: int, data: MarketUpdate | MarketFullUpdate) -> MarketFullOut:
    stmp = update(Market).where(Market.id==_id).values(**data.model_dump())
    await session.execute(stmp)
    await session.commit()
    market_db = await session.execute(select(Market).where(Market.id==_id))
    return MarketFullOut.model_validate(market_db.scalar_one(), from_attributes=True)


async def delete_market(session: AsyncSession, _id: int):
    stmp = delete(Market).where(Market.id==_id)
    await session.execute(stmp)
    await session.commit()