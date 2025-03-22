import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Type, TypeVar, Any

from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update, and_, func, text, literal_column, cast, String, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload

from src.database.db import get_db_session
from src.database.models.models import Offer
from src.database.models.models import Warehouse, OfferStock, OwnStorage, OwnStoragePlace, Market
from src.database.order_db import build_order_stats_by_warehouses
from src.database.utils import _update_or_create_object
from src.schemas.filters.stocks_filter import WarehousesFilter
from src.schemas.stocks.fbo_schemas import OfferStockOut, OfferFBOStockUpdate, AggOfferFBOStock, OfferWithStocks
from src.schemas.stocks.own_storages_schemas import OwnStorageAggOfferOut, OwnStorageOfferStockOut, OwnStorageOut, \
    OwnStorageStockOut, OwnStorageUpdate, OwnStoragePlaceCreate, OwnStoragePlaceOut, \
    OwnStoragePlaceUpdate
from src.schemas.stocks.stocks_schemas import SupplyData, GeneralOrderData
from src.schemas.stocks.warehouses_schemas import WarehouseCreate, WarehouseOut

ModelSchema = TypeVar('ModelSchema', bound=Type[BaseModel])


async def get_warehouses(session: AsyncSession, model_schema: ModelSchema = WarehouseOut,
                         filter_: WarehousesFilter | None = None) -> list[ModelSchema]:
    query = select(Warehouse)
    if filter_:
        query = filter_(query)
    result = await session.execute(query)
    return [model_schema.model_validate(warehouse_db, from_attributes=True) for warehouse_db in result.scalars().all()]


async def get_all_offers_stocks(session: AsyncSession):
    query = (
        select(
            OfferStock.id.label('id'),
            OfferStock.current_stock,
            OfferStock.offer_id,
            Warehouse.name.label('warehouse_name'),
            Offer.sku.label('sku'),
            Offer.market.label('market'),
            Offer.name_of_shop.label('name_of_shop'),
        )
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .join(Offer, Offer.id == OfferStock.offer_id)
    )
    result = (await session.execute(query)).all()
    return result


async def change_fbo_stocks(session: AsyncSession, stocks: list[OfferFBOStockUpdate]) -> None:
    for stock in stocks:
        in_box_expr = case(
            (stock.is_deliver_in_boxes, stock.in_box),
            else_=1
        )

        for_delivery_expr = case(
            (stock.min_stock > OfferStock.current_stock,
             func.ceil(
                 (stock.min_stock - OfferStock.current_stock) /
                 func.nullif(in_box_expr, 0)
             ) * in_box_expr),
            else_=0
        )

        stmp = update(OfferStock).where(OfferStock.id == stock.id).values(
            in_box=stock.in_box,
            min_stock=stock.min_stock,
            for_delivery=for_delivery_expr,
            is_deliver_in_boxes=stock.is_deliver_in_boxes,
        )
        await session.execute(stmp)

    await session.commit()


async def recalculate_stocks_for_delivery(session: AsyncSession) -> None:
    in_box_expr = case(
        (OfferStock.is_deliver_in_boxes, OfferStock.in_box),
        else_=1
    )

    for_delivery_expr = case(
        (OfferStock.min_stock > OfferStock.current_stock,
         func.ceil(
             (OfferStock.min_stock - OfferStock.current_stock) /
             func.nullif(in_box_expr, 0)
         ) * in_box_expr),
        else_=0
    )

    stmp = update(OfferStock).values(
        for_delivery=for_delivery_expr,
    )
    await session.execute(stmp)


async def update_or_create_warehouse(session: AsyncSession, data: WarehouseCreate) -> (WarehouseOut, bool):
    return await _update_or_create_object(
        session,
        Warehouse,
        data,
        and_(Warehouse.market == data.market, Warehouse.name == data.name),
        WarehouseOut
    )


async def relate_warehouses_with_clusters(session: AsyncSession, storages: list[dict]):
    for storage in storages:
        if not storage['related_warehouses_name']:
            continue

        stmp = (
            update(Warehouse).where(Warehouse.name.in_(storage['related_warehouses_name'])).where(
                Warehouse.market == 'ozon')
            .values(parent_warehouse_id=(
                select(Warehouse.id).where(Warehouse.market == 'ozon').where(Warehouse.name == storage['name'])))
        )
        await session.execute(stmp)

    stmp = text("""update offers_stocks as stock set current_stock = (
            select sum(offers_stocks.current_stock) from offers_stocks
            join warehouses on offers_stocks.warehouse_id = warehouses.id
            where warehouses.parent_warehouse_id = cluster.id and offer_id = stock.offer_id
            ) from warehouses as cluster
            where cluster.warehouse_type = 'cluster' and stock.warehouse_id = cluster.id
            """)
    await session.execute(stmp)

    stmp = update(OfferStock).options(selectinload(OfferStock.warehouse)).where(
        Warehouse.warehouse_type == 'cluster').where(OfferStock.current_stock is None).values(current_stock=0)

    await session.execute(stmp)
    await session.commit()


async def get_own_storages(session: AsyncSession, place_id: int | None = None) -> list[OwnStorageOut]:
    agg_offers_query = (
        select(
            Offer.sku,
            func.array_agg(Offer.name.distinct()).label('name'),
            func.array_agg(Offer.photo.distinct()).label('photo'),
            func.array_agg(Offer.name_of_shop.distinct()).label('name_of_shop'),
            func.array_agg(Offer.market.distinct()).label('market'),
            func.array_agg(Offer.note_1.distinct()).label('note_1'),
            func.array_agg(Offer.note_2.distinct()).label('note_2'),
            func.array_agg(Offer.note_3.distinct()).label('note_3'),
            func.array_agg(Offer.barcodes.distinct()).label('barcodes'),
        )
        .group_by(Offer.sku)
    )

    agg_offers_result = [OwnStorageAggOfferOut.model_validate(i, from_attributes=True) for i in
                         (await session.execute(agg_offers_query)).all()]

    offer_stocks_query = (
        select(
            OfferStock.offer_id,
            Offer.sku,
            Offer.market,
            Offer.name_of_shop,
            func.coalesce(func.sum(OfferStock.current_stock), 0).label('stock')
        )
        .join(Offer, Offer.id == OfferStock.offer_id)
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .where(Warehouse.warehouse_type == 'warehouse')
        .group_by(OfferStock.offer_id, Offer.sku, Offer.market, Offer.name_of_shop)
    )

    offer_stocks_result = [OwnStorageOfferStockOut.model_validate(i, from_attributes=True) for i in
                           (await session.execute(offer_stocks_query)).all()]
    stocks = defaultdict(list)
    for offer_stock in offer_stocks_result:
        stocks[offer_stock.sku].append(offer_stock)

    own_storages = select(OwnStorage)
    if place_id is not None:
        own_storages = own_storages.where(OwnStorage.storage_place_id == place_id)

    own_storages_result = [OwnStorageStockOut.model_validate(i, from_attributes=True) for i in
                           (await session.execute(own_storages)).scalars()]

    own_storages = defaultdict(list)
    for own_storage in own_storages_result:
        own_storages[own_storage.sku].append(own_storage)

    return [
        OwnStorageOut(
            offer=offer,
            storages=own_storages[offer.sku],
            stocks=stocks[offer.sku],
        )
        for offer in agg_offers_result
    ]


async def change_own_storages(session: AsyncSession, data: list[OwnStorageUpdate]):
    for storage in data:
        stmp = update(OwnStorage).where(OwnStorage.id == storage.id).where(
            OwnStorage.storage_place_id == storage.storage_place_id).values(**storage.model_dump())
        await session.execute(stmp)

    await session.commit()


async def increment_own_storage_values(session: AsyncSession, data: list[dict[str, Any]], place_id: int):
    for item in data:
        stmp = update(OwnStorage).where(OwnStorage.storage_place_id == place_id).where(
            OwnStorage.sku == item['sku']).values(value=OwnStorage.value + item['value'])
        await session.execute(stmp)
    await session.commit()


async def update_own_storages_by_sku(session: AsyncSession, data: list[dict], place_id: int):
    for storage in data:
        stmp = update(OwnStorage).where(OwnStorage.storage_place_id == place_id).where(
            OwnStorage.sku == storage['sku']).values(**storage)
        await session.execute(stmp)

    await session.commit()


def build_supply_raw_for_delivery_query(warehouses: list[int] | None = None, offers: list[int] | None = None,):
    orders_query = build_order_stats_by_warehouses().subquery()

    stocks_subquery = (
        select(
            OfferStock.offer_id.label('offer_id'),
            OfferStock.warehouse_id.label('warehouse_id'),
            OfferStock.current_stock.label('current_stock'),
            OfferStock.is_deliver_in_boxes.label('is_deliver_in_boxes'),
            OfferStock.in_box.label('in_box'),
            func.coalesce(case(
                (OfferStock.use_smart_delivery, orders_query.c.smart_delivery),
                else_=OfferStock.min_stock
            ), 0).label('min_stock'),

        )
        .select_from(OfferStock)
        .join(orders_query, and_(orders_query.c.offer_id == OfferStock.offer_id, orders_query.c.warehouse_id == OfferStock.warehouse_id), isouter=True)
    )
    stocks_subquery = stocks_subquery.subquery()

    in_box_expr = case(
        (stocks_subquery.c.is_deliver_in_boxes, stocks_subquery.c.in_box),
        else_=1
    )

    for_delivery_expr = case(
        (stocks_subquery.c.min_stock > stocks_subquery.c.current_stock,
         func.ceil(
             (stocks_subquery.c.min_stock - stocks_subquery.c.current_stock) /
             func.nullif(in_box_expr, 0)
         ) * in_box_expr),
        else_=0
    )

    query = (
        select(
            stocks_subquery.c.offer_id,
            stocks_subquery.c.warehouse_id,
            for_delivery_expr.label('for_delivery')
        )
        .select_from(stocks_subquery)
    )

    if offers:
        query = query.where(stocks_subquery.c.offer_id.in_(offers))

    if warehouses:
        query = query.where(stocks_subquery.c.warehouse_id.in_(warehouses))

    return query.subquery()


async def get_supply_only_stocks(session: AsyncSession, warehouses: list[int], offers: list[int], place_id: int):
    offer_stocks_subquery = build_supply_raw_for_delivery_query(warehouses, offers)

    offers_query = (
        select(
            Offer.sku,
            Offer.name,
            Offer.name_of_shop,
            Offer.market,
            Offer.name_of_shop,
            Offer.barcodes,
            Offer.current_price,
            (Offer.self_weight * Offer.self_length * Offer.self_height / 1000).label('volume'),
            Offer.self_weight,
            Offer.cost_price,
            offer_stocks_subquery.c.for_delivery,
            Warehouse.name.label('warehouse_name'),
            offer_stocks_subquery.c.for_delivery.label('base_for_delivery')
        )
        .join(offer_stocks_subquery, offer_stocks_subquery.c.offer_id == Offer.id)
        .join(Warehouse, Warehouse.id == offer_stocks_subquery.c.warehouse_id)
        .where(Warehouse.id.in_(warehouses))
        .where(Offer.id.in_(offers)))

    aggregated_offers_query = select(
        offers_query.c.sku,
        func.string_agg(offers_query.c.name, literal_column("','")).label('name'),
        func.avg(offers_query.c.current_price).label('current_price'),
        func.sum(offers_query.c.for_delivery).label('for_delivery'),
        func.avg(offers_query.c.volume).label('volume'),
        func.avg(offers_query.c.self_weight).label('self_weight'),
        func.avg(offers_query.c.cost_price).label('cost_price'),
        func.sum(offers_query.c.base_for_delivery).label('base_for_delivery')
    ).group_by(offers_query.c.sku)

    offers_result = (await session.execute(offers_query)).all()
    aggregated_offers_result = (await session.execute(aggregated_offers_query)).all()

    return (
        [SupplyData.model_validate(i, from_attributes=True) for i in offers_result],
        [GeneralOrderData.model_validate(i, from_attributes=True) for i in aggregated_offers_result])


async def get_supply_only_own_storage(session: AsyncSession, warehouses: list[int], offers: list[int], place_id: int):
    offer_stocks_subquery = build_supply_raw_for_delivery_query(warehouses, offers)

    own_storage_query = (select(OwnStorage.value).where(OwnStorage.storage_place_id == place_id).where(
        OwnStorage.sku == Offer.sku)).label('own_storage_value')

    offers_query = (
        select(
            Offer.sku,
            Offer.name,
            Offer.name_of_shop,
            Offer.market,
            Offer.name_of_shop,
            Offer.barcodes,
            Offer.current_price,
            (Offer.self_weight * Offer.self_length * Offer.self_height / 1000).label('volume'),
            Offer.self_weight,
            Offer.cost_price,
            Warehouse.name.label('warehouse_name'),
            func.greatest(0, func.least(offer_stocks_subquery.c.for_delivery, (own_storage_query - func.coalesce(
                func.sum(offer_stocks_subquery.c.for_delivery).over(partition_by=Offer.sku, order_by=offer_stocks_subquery.c.for_delivery.desc(),
                                                       rows=(None, -1)), 0)))).label('for_delivery'),
            offer_stocks_subquery.c.for_delivery.label('base_for_delivery')
        )
        .join(offer_stocks_subquery, offer_stocks_subquery.c.offer_id == Offer.id)
        .join(Warehouse, Warehouse.id == offer_stocks_subquery.c.warehouse_id)
        .where(Warehouse.id.in_(warehouses))
        .where(Offer.id.in_(offers))
    )

    aggregated_offers_query = select(
        offers_query.c.sku,
        func.string_agg(offers_query.c.name, literal_column("','")).label('name'),
        func.avg(offers_query.c.current_price).label('current_price'),
        func.sum(offers_query.c.for_delivery).label('for_delivery'),
        func.avg(offers_query.c.volume).label('volume'),
        func.avg(offers_query.c.self_weight).label('self_weight'),
        func.avg(offers_query.c.cost_price).label('cost_price'),
        (select(OwnStorage.value).where(OwnStorage.storage_place_id == place_id).where(
            OwnStorage.sku == offers_query.c.sku)).label('own_storage_value'),
        func.sum(offers_query.c.base_for_delivery).label('base_for_delivery')
    ).group_by(offers_query.c.sku)

    offers_result = (await session.execute(offers_query)).all()
    aggregated_offers_result = (await session.execute(aggregated_offers_query)).all()

    return (
        [SupplyData.model_validate(i, from_attributes=True) for i in offers_result],
        [GeneralOrderData.model_validate(i, from_attributes=True) for i in aggregated_offers_result])


async def update_fbo_support_data(session: AsyncSession, data: list[dict], name_of_shop: str, warehouse_id: int):
    now = datetime.now()
    for stock in data:
        sub_query = (
            select(OfferStock.id)
            .join(Offer, Offer.id == OfferStock.offer_id)
            .where(OfferStock.warehouse_id == warehouse_id)
            .where(Offer.sku == str(stock['sku']))
        )

        stmp = update(OfferStock).where(OfferStock.id.in_(sub_query)).values(
            **{'can_be_delivered': stock['can_be_delivered'], 'advice_from_the_store': stock['advice_from_the_store']})
        await session.execute(stmp)
        stmp = update(Warehouse).where(Warehouse.id == warehouse_id).values(from_file_updated_at=now)
        await session.execute(stmp)

    await session.commit()


async def get_warehouse(session: AsyncSession, warehouse_id: int, model_schema: Type[ModelSchema] = WarehouseOut,
                        allow_none: bool = True) -> WarehouseOut | None:
    query = select(Warehouse).where(Warehouse.id == warehouse_id)
    result = (await session.execute(query)).scalar_one_or_none()

    if not result:
        if allow_none:
            return None

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Warehouse with id - {warehouse_id} not found")

    return model_schema.model_validate(result, from_attributes=True)


async def create_own_storage_stocks(session: AsyncSession):
    places_query = select(OwnStoragePlace.id)
    places = [i[0] for i in (await session.execute(places_query)).all()]

    for place_id in places:
        sub_query = select(OwnStorage.sku).where(OwnStorage.storage_place_id == place_id).distinct()
        query = select(Offer.sku).distinct().where(Offer.sku.not_in(sub_query))
        result = (await session.execute(query)).all()
        skus = [i[0] for i in result]

        session.add_all([OwnStorage(sku=sku, value=0, storage_place_id=place_id) for sku in skus])
        await session.commit()


async def create_own_storage_places(session: AsyncSession, data: list[OwnStoragePlaceCreate]):
    db_storages = [OwnStoragePlace(**i.model_dump()) for i in data]
    session.add_all(db_storages)
    await session.commit()


async def get_all_own_storage_places(session: AsyncSession) -> list[OwnStoragePlaceOut]:
    query = select(OwnStoragePlace)
    result = await session.execute(query)
    return [OwnStoragePlaceOut.model_validate(i, from_attributes=True) for i in result.scalars()]


async def get_own_storage_place(session: AsyncSession, place_id: int,
                                allow_none: bool = False) -> OwnStoragePlaceOut | None:
    query = select(OwnStoragePlace).where(OwnStoragePlace.id == place_id)
    result = (await session.execute(query)).scalar_one_or_none()

    if not result:
        if allow_none:
            return None
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f'Моего склада с id - {place_id} не найдено')

    return OwnStoragePlaceOut.model_validate(result, from_attributes=True)


async def change_own_storage_places(session: AsyncSession, data: list[OwnStoragePlaceUpdate]):
    for place in data:
        stmp = update(OwnStoragePlace).where(OwnStoragePlace.id == place.id).values(**place.model_dump())
        await session.execute(stmp)

    await session.commit()


async def create_fbo_stocks_(session: AsyncSession, data: list[dict]):
    new_db_stocks = [OfferStock(**i) for i in data]
    session.add_all(new_db_stocks)
    await session.commit()


async def recalculate_clusters_stocks(session: AsyncSession):
    stocks_subquery = (
        select(
            OfferStock.offer_id,
            Warehouse.parent_warehouse_id,
            func.sum(OfferStock.current_stock).label('current_stock')
        )
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .group_by(OfferStock.offer_id, Warehouse.parent_warehouse_id)
        .where(Warehouse.warehouse_type == 'warehouse')
        .where(Warehouse.parent_warehouse_id is not None)
    ).subquery('stocks_subquery')

    current_cluster_stock_subquery = (
        select(
            OfferStock.id,
            stocks_subquery.c.current_stock
        )
        .select_from(stocks_subquery)
        .join(OfferStock, and_(OfferStock.offer_id == stocks_subquery.c.offer_id,
                               OfferStock.warehouse_id == stocks_subquery.c.parent_warehouse_id))
    ).subquery('current_cluster_stock_subquery')

    stmp = (
        update(OfferStock)
        .where(OfferStock.id == current_cluster_stock_subquery.c.id)
        .values(current_stock=current_cluster_stock_subquery.c.current_stock)
    )
    await session.execute(stmp)
    await session.commit()


async def recalculate_super_clusters_stocks(session: AsyncSession):
    stocks_subquery = (
        select(
            OfferStock.offer_id,
            func.sum(OfferStock.current_stock).label('current_stock')
        )
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .where(Warehouse.warehouse_type == 'warehouse')
        .group_by(OfferStock.offer_id)
    ).subquery('stocks_subquery')

    current_super_cluster_stock_subquery = (
        select(
            OfferStock.id,
            stocks_subquery.c.current_stock
        )
        .join(stocks_subquery, stocks_subquery.c.offer_id == OfferStock.offer_id)
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .where(Warehouse.warehouse_type == 'super_cluster')
    )

    stmp = (
        update(OfferStock)
        .where(OfferStock.id == current_super_cluster_stock_subquery.c.id)
        .values(current_stock=current_super_cluster_stock_subquery.c.current_stock)
    )

    await session.execute(stmp)
    await session.commit()


# async def recalculate_clusters(session: AsyncSession):
#     clusters_subquery = (
#         select(
#             Warehouse.parent_warehouse_id.label('id'),
#             func.sum(OfferStock.current_stock).label('current_stock')
#         )
#         .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
#         .where(Warehouse.warehouse_type == 'warehouse')
#         .group_by(Warehouse.parent_warehouse_id)
#     ).subquery('clusters_subquery')
#
#     clusters_stmp = (
#         update(OfferStock)
#         .where(OfferStock.warehouse_id == clusters_subquery.c.id)
#         .values(
#             current_stock=clusters_subquery.c.current_stock
#         )
#     )
#     await session.execute(clusters_stmp)
#
#     super_clusters_subquery = (
#         select(
#             Warehouse.id.label('id'),
#             func.sum(OfferStock.current_stock).label('current_stock')
#         )
#         .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
#         .where(Warehouse.warehouse_type == 'warehouse')
#         .group_by(Warehouse.id)
#     ).subquery('super_clusters_subquery')
#
#     super_clusters_stmp = (
#         update(OfferStock)
#         .where(OfferStock.warehouse_id == super_clusters_subquery.c.id)
#         .values(
#             current_stock=super_clusters_subquery.c.current_stock
#         )
#     )
#
#     await session.execute(super_clusters_stmp)
#
#     await session.commit()


async def update_fbo_stocks(session: AsyncSession, data: list[dict]):
    for stock in data:
        stmp = update(OfferStock).values(current_stock=stock['current_stock']).where(OfferStock.id == stock['id'])
        await session.execute(stmp)

    await session.commit()


async def fill_empty_stocks(session: AsyncSession):
    markets_query = select(
        func.upper(cast(Market.type, String)).label('market'),
        func.array(
            (select(Warehouse.id).where(
                func.upper(cast(Warehouse.market, String)) == func.upper(cast(Market.type, String))))
        ).label('warehouses')
    )
    markets_warehouses = {i.market: set(i.warehouses) for i in (await session.execute(markets_query)).all()}

    query = select(
        Offer.id,
        Offer.sku,
        func.upper(cast(Offer.market, String)).label('market'),
        Offer.name_of_shop,
        func.array(
            (select(OfferStock.warehouse_id).where(OfferStock.offer_id == Offer.id))
        ).label('warehouses')
    )
    result = (await session.execute(query)).all()

    for item in result:
        if len(markets_warehouses[item.market]) == len(set(item.warehouses)):
            continue

        to_set_warehouses_stocks = markets_warehouses[item.market] - set(item.warehouses)

        new_stocks = [OfferStock(offer_id=item.id, warehouse_id=warehouse_id, current_stock=0) for warehouse_id in
                      to_set_warehouses_stocks]
        session.add_all(new_stocks)

        await session.commit()


async def get_offer_fbo_stocks(session: AsyncSession, offer_id: int) -> list[OfferWithStocks]:
    query = select(OfferStock).where(OfferStock.offer_id == offer_id)
    result = (await session.execute(query)).scalars()
    return [OfferStockOut.model_validate(i, from_attributes=True) for i in result]

async def get_fbo_offers(session: AsyncSession):
    query = (
        select(Offer)
        .options(subqueryload(Offer.stocks)
                 .selectinload(OfferStock.warehouse)
                 )
    )
    result = await session.execute(query)
    offers = result.scalars().all()


    return [OfferWithStocks.model_validate(i, from_attributes=True) for i in offers]

async def offer_stocks_list(session: AsyncSession, chunk_size: int | None = None, offset: int | None = 0):
    query = select(OfferStock.offer_id, OfferStock.current_stock)

    while True:
        query = query.limit(chunk_size).offset(offset)
        chunk = (await session.execute(query)).all()
        res = [{item[0]: item[1]} for item in chunk]

        if len(res) == 0:
            return

        yield res

        if chunk_size is None:
            return
        offset += chunk_size


async def get_agg_fbo_data(session: AsyncSession, warehouse_ids: list[int] | None = None,
                           ignore_clusters: bool = True) -> list[AggOfferFBOStock]:
    query = (
        select(
            OfferStock.offer_id,
            func.sum(OfferStock.min_stock).label('min_stock'),
            func.sum(OfferStock.current_stock).label('current_stock'),
            func.sum(OfferStock.for_delivery).label('for_delivery')
        )
        .group_by(OfferStock.offer_id)
    )

    if warehouse_ids:
        query = query.where(OfferStock.offer_id.in_(warehouse_ids))

    if ignore_clusters:
        query = query.join(Warehouse, Warehouse.id == OfferStock.warehouse_id).where(
            Warehouse.warehouse_type == 'warehouse')

    results = (await session.execute(query)).all()
    return [AggOfferFBOStock.model_validate(i, from_attributes=True) for i in results]
