from datetime import datetime

from pydantic import create_model
from sqlalchemy import select, func, text, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.database.models.models import Order, Offer, OfferStock, Market, Warehouse
from src.schemas.filters.filter_schemas import PagingFilter
from src.schemas.filters.orders_filter import OrderFilter
from src.schemas.filters.statistic_filter import OrderStatisticFilter
from src.schemas.orders_scemas import OrderCreate, OrderOut, \
    OrdersQuantityStatOnlyOffers, OrdersQuantityStatOffersWithWarehouses


async def create_orders(session: AsyncSession, orders: list[OrderCreate]) -> None:
    new_order = [Order(**order.model_dump()) for order in orders]
    session.add_all(new_order)
    await session.commit()


async def get_orders(session: AsyncSession, filter_: OrderFilter | None = None, paging: PagingFilter | None = None) -> list[OrderOut]:
    query = select(Order).order_by(Order.created_at.desc())

    if filter_:
        query = filter_(query)

    if paging:
        query = paging(query)

    result = (await session.execute(query)).scalars()
    return [OrderOut.model_validate(i, from_attributes=True) for i in result]


def _build_quantity_offers_query(name: str, days_interval: int, offer_ids: list[int] | None = None):
    query = select(
        Order.offer_id,
        func.sum(Order.quantity).label(name),
    ).where(Order.created_at >= text(f"NOW() - INTERVAL '{days_interval} days'"))

    if offer_ids:
        query = query.where(Order.offer_id.in_(offer_ids))

    query = query.group_by(Order.offer_id).subquery()
    return query


async def aggregate_orders_quantity_by_offers(session: AsyncSession, filter: OrderStatisticFilter):
    query_periods = {
        'today': _build_quantity_offers_query('today', 0, filter.offer_ids),
        'yesterday': _build_quantity_offers_query('yesterday', 1, filter.offer_ids),
        'for_7_days': _build_quantity_offers_query('for_7_days', 7, filter.offer_ids),
        'for_14_days': _build_quantity_offers_query('for_14_days', 14, filter.offer_ids),
        'for_28_days': _build_quantity_offers_query('for_28_days', 28, filter.offer_ids),
        'for_60_days': _build_quantity_offers_query('for_60_days', 60, filter.offer_ids),
        'for_120_days': _build_quantity_offers_query('for_120_days', 120, filter.offer_ids),
    }

    main_query = (
        select(
            Offer.id.label('offer_id'),
            *[func.coalesce(getattr(subquery.c, subquery_name), 0).label(subquery_name)
              for subquery_name, subquery in query_periods.items()],
            _build_smart_delivery_query(query_periods).label('smart_delivery')
        )
        .select_from(Offer)
        .join(Market, and_(Market.name == Offer.name_of_shop, Market.type == Offer.market))
    )

    for subquery in query_periods.values():
        main_query = main_query.join(subquery, subquery.c.offer_id == Offer.id, isouter=True)

    if filter.offer_ids:
        main_query = main_query.where(Offer.id.in_(filter.offer_ids))

    result = (await session.execute(main_query)).all()

    return [OrdersQuantityStatOnlyOffers.model_validate(i, from_attributes=True) for i in result]


def _build_smart_delivery_query(period_queries: dict):
    market_variables = [Market.a_variable_for_smart_delivery, Market.b_variable_for_smart_delivery,
                        Market.c_variable_for_smart_delivery, Market.d_variable_for_smart_delivery,
                        Market.e_variable_for_smart_delivery]
    period_names = ['for_7_days', 'for_14_days', 'for_28_days', 'for_60_days', 'for_120_days']

    return sum([var * func.coalesce(getattr(period_queries[period_name].c, period_name), 0) for var, period_name in zip(market_variables, period_names)])


def _build_quantity_warehouses_query(name: str, days_interval: int, offer_ids: list[int] | None = None, warehouse_ids: list[int] | None = None):
    warehouses_query = (
        select(
            Order.offer_id,
            Order.warehouse_id,
            func.sum(Order.quantity).label(name),
        )
        .join(Warehouse, Warehouse.id == Order.warehouse_id)
        .where(Order.warehouse_id.is_not(None))
        .where(Warehouse.parent_warehouse_id == None)
        .where(Order.created_at >= text(f"NOW() - INTERVAL '{days_interval} days'"))
    )

    if offer_ids:
        warehouses_query = warehouses_query.where(Order.offer_id.in_(offer_ids))

    if warehouse_ids:
        warehouses_query = warehouses_query.where(Order.warehouse_id.in_(warehouse_ids))

    warehouses_query = warehouses_query.group_by(Order.offer_id, Order.warehouse_id)

    clusters_query = (
        select(
            Warehouse.parent_warehouse_id,
            Order.offer_id,
            func.sum(Order.quantity).label(name)
        )
        .join(Warehouse, Warehouse.id == Order.warehouse_id)
        .where(Warehouse.parent_warehouse_id != None)
        .where(Order.created_at >= text(f"NOW() - INTERVAL '{days_interval} days'"))
    )

    if warehouse_ids:
        clusters_query = clusters_query.where(Warehouse.parent_warehouse_id.in_(warehouse_ids))

    if offer_ids:
        clusters_query = clusters_query.where(Order.offer_id.in_(offer_ids))

    clusters_query = clusters_query.group_by(Warehouse.parent_warehouse_id, Order.offer_id)

    super_cluster_query = (
        select(
            Order.offer_id,
            func.sum(Order.quantity).label(name),
            Warehouse.id
        )
        .join(Offer, Offer.id == Order.offer_id)
        .join(Warehouse, and_(Warehouse.warehouse_type == 'super_cluster', Warehouse.market == Offer.market))
    )

    if warehouse_ids:
        super_cluster_query = super_cluster_query.where(Warehouse.id.in_(warehouse_ids))

    if offer_ids:
        super_cluster_query = super_cluster_query.where(Order.offer_id.in_(offer_ids))

    super_cluster_query = super_cluster_query.group_by(Warehouse.id, Order.offer_id)

    result_query = warehouses_query.union(clusters_query, super_cluster_query).subquery()
    return result_query


async def aggregate_orders_quantity_by_offers_with_warehouses(session: AsyncSession, filter: OrderStatisticFilter):
    query_periods = {
        'today': _build_quantity_warehouses_query('today', 0, filter.offer_ids, filter.warehouse_ids),
        'yesterday': _build_quantity_warehouses_query('yesterday', 1, filter.offer_ids, filter.warehouse_ids),
        'for_7_days': _build_quantity_warehouses_query('for_7_days', 7, filter.offer_ids, filter.warehouse_ids),
        'for_14_days': _build_quantity_warehouses_query('for_14_days', 14, filter.offer_ids, filter.warehouse_ids),
        'for_28_days': _build_quantity_warehouses_query('for_28_days', 28, filter.offer_ids, filter.warehouse_ids),
        'for_60_days': _build_quantity_warehouses_query('for_60_days', 60, filter.offer_ids, filter.warehouse_ids),
        'for_120_days': _build_quantity_warehouses_query('for_120_days', 120, filter.offer_ids, filter.warehouse_ids),
    }

    main_query = (
        select(
            OfferStock.offer_id.label('offer_id'),
            OfferStock.warehouse_id.label('warehouse_id'),
            *[func.coalesce(getattr(subquery.c, subquery_name), 0).label(subquery_name)
              for subquery_name, subquery in query_periods.items()],
            _build_smart_delivery_query(query_periods).label('smart_delivery')
        )
        .select_from(OfferStock)
        .join(Offer, Offer.id == OfferStock.offer_id)
        .join(Market, and_(Market.name == Offer.name_of_shop, Market.type == Offer.market))
    )
    for subquery in query_periods.values():
        main_query = main_query.join(subquery, and_(subquery.c.offer_id == OfferStock.offer_id,
                                                    subquery.c.warehouse_id == OfferStock.warehouse_id), isouter=True)

    if filter.offer_ids:
        main_query = main_query.where(OfferStock.offer_id.in_(filter.offer_ids))

    if filter.warehouse_ids:
        main_query = main_query.where(OfferStock.warehouse_id.in_(filter.warehouse_ids))

    result = (await session.execute(main_query)).all()

    return [OrdersQuantityStatOffersWithWarehouses.model_validate(i, from_attributes=True) for i in result]
