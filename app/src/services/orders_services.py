import pandas as pd
from fastapi import HTTPException
from starlette import status

from src.api.wrapper import APIWrapper
from datetime import datetime, timedelta
from src.database import warehouse_db, offer_db
from src.database.db import async_session
from src.database.models.models import Offer
from src.schemas.filters.statistic_filter import OrderStatisticFilter
from src.schemas.orders_scemas import OrderCreate, OrderOut
from src.database import order_db as db

api_wrapper = APIWrapper()


async def setup_orders() -> None:
    end = datetime.now()
    start = end - timedelta(days=120)

    async with async_session() as session:
        offers_idents = await offer_db.get_offers_fields(session, [Offer.id, Offer.sku, Offer.market, Offer.name_of_shop])
        if not offers_idents:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для получения остатков требуется наличие товаров')

        db_warehouses = await warehouse_db.get_warehouses(session)
        if not db_warehouses:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для получения остатков требуется наличие складов')

    api_orders = await api_wrapper.get_orders(start, end)
    api_orders_df = pd.DataFrame([i.model_dump() for i in api_orders])
    warehouses_df = pd.DataFrame([i.model_dump() for i in db_warehouses])
    warehouses_df.rename(columns={
        'id': 'warehouse_id',
        'name': 'warehouse_name',
    }, inplace=True)
    offers_idents_df = pd.DataFrame(offers_idents)
    offers_idents_df.rename(columns={'id': 'offer_id'}, inplace=True)

    merged_orders = pd.merge(api_orders_df, warehouses_df[['warehouse_id', 'warehouse_name']], on='warehouse_name', how='inner')
    merged_orders = pd.merge(merged_orders, offers_idents_df, how='inner', on=['sku', 'market', 'name_of_shop'])
    merged_orders['created_at'] = merged_orders['created_at'].apply(lambda x: x.replace(tzinfo=None))
    merged_orders['updated_at'] = merged_orders['updated_at'].apply(lambda x: x.replace(tzinfo=None))
    new_orders = [OrderCreate(**i) for i in merged_orders.to_dict('records')]

    async with async_session() as session:
        await db.create_orders(session, new_orders)


async def get_orders() -> list[OrderOut]:
    async with async_session() as session:
        return await db.get_orders(session)


async def get_order_statistics(filter: OrderStatisticFilter):
    async with async_session() as session:
        if filter.group_by_warehouses:
            return await db.aggregate_orders_quantity_by_warehouses(session, filter)
        else:
            return await db.aggregate_orders_quantity_by_offers(session, filter)






