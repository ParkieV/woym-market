import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, ColumnElement
from sqlalchemy.orm import selectinload, subqueryload
from sqlalchemy.sql import func
from src.database.models.base import Base
from src.schemas.stocks_schemas import WarehouseCreate, OfferStockCreate, WarehouseOut, OfferStockOut, OfferWithStocks, \
    OfferStockWithWarehouseOut, OfferWithStocksUpdate, OfferStockUpdate
from src.database.models.models import Warehouse, OfferStock
from pydantic import BaseModel
from src.database.models.models import Offer
from typing import Type, TypeVar, Any

ModelSchema = TypeVar('ModelSchema', bound=Type[BaseModel])


async def create_warehouse(session: AsyncSession, data: WarehouseCreate, model_schema: ModelSchema = WarehouseOut) -> ModelSchema:
    warehouse_db = Warehouse(**data.model_dump())
    session.add(warehouse_db)
    await session.commit()
    return model_schema.model_validate(warehouse_db, from_attributes=True)


async def get_warehouses(session: AsyncSession, model_schema: ModelSchema = WarehouseOut) -> list[ModelSchema]:
    query = select(Warehouse)
    result = await session.execute(query)
    return [model_schema.model_validate(warehouse_db, from_attributes=True) for warehouse_db in result.scalars().all()]


async def create_offer_stock(session: AsyncSession, data: OfferStockCreate, model_schema: ModelSchema = OfferStockOut) -> ModelSchema:
    offer_stock_db = OfferStock(**data.model_dump())
    session.add(offer_stock_db)
    await session.commit()
    return model_schema.model_validate(offer_stock_db, from_attributes=True)


async def get_offers_stocks(session: AsyncSession, model_schema: ModelSchema = OfferStockWithWarehouseOut) -> list[ModelSchema]:
    query = select(OfferStock).where(OfferStock.offer_id==1).options(selectinload(OfferStock.warehouse))
    result = await session.execute(query)
    return [model_schema.model_validate(offer_stock_db, from_attributes=True) for offer_stock_db in result.scalars().all()]


async def get_offer_stock_by_id(session: AsyncSession, _id: int, model_schema: ModelSchema = OfferStockOut) -> ModelSchema:
    query = select(OfferStock).where(OfferStock.id==_id)
    result = await session.execute(query)
    return model_schema.model_validate(result.scalar_one(), from_attributes=True)


async def get_offers_with_stocks(session: AsyncSession, model_schema: ModelSchema = OfferWithStocks) -> list[ModelSchema]:
    query = (
        select(Offer)
        .options(subqueryload(Offer.stocks).subqueryload(OfferStock.warehouse))

    )
    result = await session.execute(query)
    return [model_schema.model_validate(offer, from_attributes=True) for offer in result.scalars().all()]


async def change_offer_with_stock(session: AsyncSession, data: list[OfferWithStocksUpdate]):
    for offer_with_stock in data:
        offer_data = offer_with_stock.model_dump()
        offer_data.pop('stocks')

        stmp = update(Offer).where(Offer.id==offer_data['id']).values(**offer_data)
        await session.execute(stmp)

        for stock in offer_with_stock.stocks:
            stock_data = stock.model_dump()
            
            db_stock = await get_offer_stock_by_id(session, stock_data['id'])
            for_delivery = stock_data['min_stock'] - db_stock.current_stock
            for_delivery = 0 if for_delivery < 0 else for_delivery

            stmp = update(OfferStock).where(OfferStock.id==stock_data['id']).values(for_delivery=for_delivery, **stock_data)
            await session.execute(stmp)

    await session.commit()


async def _update_or_create_object(
        session: AsyncSession,
        model: Type[Base],
        data: BaseModel,
        update_by:  ColumnElement[bool],
        model_schema: Type[BaseModel]
) -> (Any, bool):
    query = select(model).filter_by(**data.model_dump())
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


async def update_or_create_warehouse(session: AsyncSession, data: WarehouseCreate) -> (WarehouseOut, bool):
    return await _update_or_create_object(
        session,
        Warehouse,
        data,
        and_(Warehouse.market==data.market, Warehouse.warehouse_id_in_marketplace==data.warehouse_id_in_marketplace),
        WarehouseOut
    )


async def update_or_create_offer_stock(session: AsyncSession, data: OfferStockCreate) -> (OfferStockOut, bool):
    return await _update_or_create_object(
        session,
        OfferStock,
        data,
        and_(OfferStock.offer_id == data.offer_id,
             OfferStock.warehouse_id == data.warehouse_id),
        OfferStockOut
    )


async def test_own_storage(session: AsyncSession, sku: str):
    query = (
        select(
            Offer.sku,
            func.array_agg(Offer.photo),
            func.array_agg(Offer.name),
            func.array_agg(Offer.note_1),
            func.array_agg(Offer.note_2),
            func.array_agg(Offer.note_3),
            )

        .where(Offer.sku==sku)
        .group_by(Offer.sku)
    )
    result = (await session.execute(query)).first()
    return {'sku': result[0], 'photo': set(result[1]), 'name': set(result[2]), 'note_1': set(result[3]), 'note_2': set(result[4]), 'note_3': set(result[5])}

