from src.database.db import async_session
from src.database import warehouse_db as db
from src.database import offer_db
from src.api.factory import APIFactory, APITypes
from src.params.confing import config
from src.schemas.stocks_schemas import WarehouseCreate, WarehouseOut, OfferStockOut, OfferStockCreate, OfferWithStocksUpdate
from fastapi import status
from fastapi.exceptions import HTTPException



async def setup_warehouses_and_stocks():
    stocks = await yandex_api.get_stocks()

    async with async_session() as session:

        for warehouse in stocks:
            warehouse_db = await db.create_warehouse(session, WarehouseCreate(
                name=warehouse.name,
                warehouse_id_in_marketplace=warehouse.warehouse_id,
                market=warehouse.market
            ))

            for offer_stock in warehouse.offers:
                offer = await offer_db.get_offer(session, {'sku': offer_stock.sku, 'name_of_shop': offer_stock.name_of_shop, 'market': warehouse.market})

                offer_stock_create = OfferStockCreate(
                    current_stock=offer_stock.current_stock,
                    warehouse_id=warehouse_db.id,
                    offer_id=offer.id
                )
                await db.create_offer_stock(session, offer_stock_create)


async def get_warehouses():
    async with async_session() as session:
        return await db.get_warehouses(session)


async def get_offers_stocks():
    async with async_session() as session:
        return await db.get_offers_stocks(session)


async def get_offers_with_stocks():
    async with async_session() as session:
        return await db.get_offers_with_stocks(session)


async def change_offer_with_stock(data: list[OfferWithStocksUpdate]):
    async with async_session() as session:
        await db.change_offer_with_stock(session, data)

