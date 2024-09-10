from datetime import datetime

from pydantic import create_model
from sqlalchemy import select, func, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models import Order, Offer, OfferStock
from src.schemas.filters.orders_filter import OrderFilter
from src.schemas.filters.statistic_filter import OrderStatisticFilter, GroupStatFilter
from src.schemas.orders_scemas import OrderCreate, OrderOut, OffersOrderQuantity, OrdersQuantityPeriodStatistic


async def create_orders(session: AsyncSession, orders: list[OrderCreate]) -> None:
    new_order = [Order(**order.model_dump()) for order in orders]
    session.add_all(new_order)
    await session.commit()


async def get_orders(session: AsyncSession, filter: OrderFilter | None) -> list[OrderOut]:
    query = select(Order)

    if filter:
        query = filter.filter(query)

    result = (await session.execute(query)).scalars()
    return [OrderOut.model_validate(i, from_attributes=True) for i in result]


def _build_quantity_offers_query(name: str, days_interval: int, offer_ids: list[int]):
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

    main_query = select(
        Offer.id.label('offer_id'),
        *[
            func.coalesce(getattr(subquery.c, subquery_name), 0).label(subquery_name)
            for subquery_name, subquery in query_periods.items()
        ]
    )
    for subquery in query_periods.values():
        main_query = main_query.join(subquery, subquery.c.offer_id == Offer.id, isouter=True)

    if filter.offer_ids:
        main_query = main_query.where(Offer.id.in_(filter.offer_ids))

    result = (await session.execute(main_query)).all()

    return [OrdersQuantityPeriodStatistic.model_validate(i, from_attributes=True) for i in result]


def _build_quantity_warehouses_query(name: str, days_interval: int, offer_ids: list[int], warehouse_ids: list[int]):
    query = select(
                Order.offer_id,
                Order.warehouse_id,
                func.sum(Order.quantity).label(name),
            ).where(Order.created_at >= text(f"NOW() - INTERVAL '{days_interval} days'"))

    if offer_ids:
        query = query.where(Order.offer_id.in_(offer_ids))

    if warehouse_ids:
        query = query.where(Order.warehouse_id.in_(warehouse_ids))

    query = query.group_by(Order.offer_id, Order.warehouse_id).subquery()

    return query


async def aggregate_orders_quantity_by_warehouses(session: AsyncSession, filter: OrderStatisticFilter):
    query_periods = {
        'today': _build_quantity_warehouses_query('today', 0, filter.offer_ids, filter.warehouse_ids),
        'yesterday': _build_quantity_warehouses_query('yesterday', 1, filter.offer_ids, filter.warehouse_ids),
        'for_7_days': _build_quantity_warehouses_query('for_7_days', 7, filter.offer_ids, filter.warehouse_ids),
        'for_14_days': _build_quantity_warehouses_query('for_14_days', 14, filter.offer_ids, filter.warehouse_ids),
        'for_28_days': _build_quantity_warehouses_query('for_28_days', 28, filter.offer_ids, filter.warehouse_ids),
        'for_60_days': _build_quantity_warehouses_query('for_60_days', 60, filter.offer_ids, filter.warehouse_ids),
        'for_120_days': _build_quantity_warehouses_query('for_120_days', 120, filter.offer_ids, filter.warehouse_ids),
    }

    main_query = select(
        OfferStock.offer_id.label('offer_id'),
        OfferStock.warehouse_id.label('warehouse_id'),
        *[
            func.coalesce(getattr(subquery.c, subquery_name), 0).label(subquery_name)
            for subquery_name, subquery in query_periods.items()
        ]
    )
    for subquery in query_periods.values():
        main_query = main_query.join(subquery, and_(subquery.c.offer_id == OfferStock.offer_id, subquery.c.warehouse_id == OfferStock.warehouse_id), isouter=True)

    if filter.offer_ids:
        main_query = main_query.where(OfferStock.offer_id.in_(filter.offer_ids))

    if filter.warehouse_ids:
        main_query = main_query.where(OfferStock.warehouse_id.in_(filter.warehouse_ids))

    result = (await session.execute(main_query)).all()

    return [OrdersQuantityPeriodStatistic.model_validate(i, from_attributes=True) for i in result]

