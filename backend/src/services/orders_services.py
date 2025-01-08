import numpy as np
import pandas as pd
from fastapi import HTTPException
from starlette import status

from logs import get_logger
from src.api.wrapper import APIWrapper
from datetime import datetime, timedelta
from src.database import warehouse_db, offer
from src.database.db import async_session
from src.database.models.models import Offer
from src.schemas.filters.filter_schemas import PagingFilter
from src.schemas.filters.orders_filter import OrderFilter
from src.schemas.filters.statistic_filter import OrderStatisticFilter
from src.schemas.orders_scemas import OrderCreate, OrderOut
from src.database import order_db as db

api_wrapper = APIWrapper()

logger = get_logger(__name__)


async def setup_orders() -> None:
    end = datetime.now()
    start = end - timedelta(days=120)

    async with async_session() as session:
        offers_idents = await offer.get_offers_fields(session, [Offer.id, Offer.sku, Offer.market, Offer.name_of_shop])
        if not offers_idents:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для получения остатков требуется наличие товаров')

        db_warehouses = await warehouse_db.get_warehouses(session)
        if not db_warehouses:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для получения остатков требуется наличие складов')
        
        db_orders = await db.get_orders(session)
        db_orders_df = pd.DataFrame([i.model_dump() for i in db_orders], columns=OrderOut.model_fields.keys())

    api_orders = await api_wrapper.get_orders(start, end)
    api_orders_df = pd.DataFrame([i.model_dump() for i in api_orders])
    warehouses_df = pd.DataFrame([i.model_dump() for i in db_warehouses])
    warehouses_df.rename(columns={
        'id': 'warehouse_id',
        'name': 'warehouse_name',
    }, inplace=True)
    offers_idents_df = pd.DataFrame(offers_idents)
    offers_idents_df.rename(columns={'id': 'offer_id'}, inplace=True)

    new_api_orders = pd.merge(api_orders_df, warehouses_df[['warehouse_id', 'warehouse_name']], on='warehouse_name', how='left')
    new_api_orders = pd.merge(new_api_orders, offers_idents_df, how='inner', on=['sku', 'market', 'name_of_shop'])
    new_api_orders['created_at'] = new_api_orders['created_at'].apply(lambda x: x.replace(tzinfo=None))
    new_api_orders['updated_at'] = new_api_orders['updated_at'].apply(lambda x: x.replace(tzinfo=None))

    merged_orders = pd.merge(new_api_orders, db_orders_df, on=['offer_id', 'internal_order_id'], indicator=True, how='outer', suffixes=(None, '__db'))
    merged_orders['warehouse_id'] = merged_orders['warehouse_id'].replace({np.nan: None})

    to_create_orders = merged_orders[merged_orders['_merge'] == 'left_only']
    to_create_orders.drop(columns=['id', '_merge'], inplace=True)

    new_orders = [OrderCreate(**i) for i in to_create_orders.to_dict('records')]

    if not new_orders:
        logger.info('New orders not found')
        return

    async with async_session() as session:
        await db.create_orders(session, new_orders)
        logger.info(f'New orders created: {len(new_orders)}')


async def get_orders(filter_: OrderFilter | None, paging: PagingFilter | None) -> list[OrderOut]:
    async with async_session() as session:
        return await db.get_orders(session, filter_, paging)


async def get_order_statistics_by_offers_with_warehouses(filter_: OrderStatisticFilter):
    async with async_session() as session:
        return await db.aggregate_orders_quantity_by_offers_with_warehouses(session, filter_)
        
        
async def get_orders_statistics_by_offers(filter_: OrderStatisticFilter):
    async with async_session() as session:
        return await db.aggregate_orders_quantity_by_offers(session, filter_)





