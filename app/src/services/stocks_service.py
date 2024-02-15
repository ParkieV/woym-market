from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import warehouse_db as db
from src.database import offer_db
from src.schemas.stocks_schemas import WarehouseCreate, WarehouseOut, OfferStockOut, OfferStockCreate, OfferWithStocksUpdate


api_wrapper = APIWrapper()


async def update_warehouses_and_stocks():
    stocks = await api_wrapper.get_stocks()

    async with async_session() as session:

        for warehouse in stocks:
            warehouse_db, _ = await db.update_or_create_warehouse(session, WarehouseCreate(
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
                await db.update_or_create_offer_stock(session, offer_stock_create)


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


async def test_own_storage(sku: str):
    async with async_session() as session:
        return await db.test_own_storage(session, sku)

