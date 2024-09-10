from datetime import datetime

from pydantic import create_model
from sqlalchemy import select, func, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models import Order, Offer, OfferStock
from src.schemas.filters.statistic_filter import OrderStatisticFilter, GroupStatFilter
from src.schemas.orders_scemas import OrderCreate, OrderOut, OffersOrderQuantityStat


async def create_orders(session: AsyncSession, orders: list[OrderCreate]) -> None:
    new_order = [Order(**order.model_dump()) for order in orders]
    session.add_all(new_order)
    await session.commit()


async def get_orders(session: AsyncSession) -> list[OrderOut]:
    query = select(Order)
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
    period_stats_queries = {
        period.field_name: _build_quantity_offers_query(period.field_name, period.days_interval, filter.offer_ids)
        for period in filter.periods
    }

    main_query = select(
        Offer.id.label('offer_id'),
        *[
            func.coalesce(getattr(subquery.c, subquery_name), 0).label(subquery_name)
            for subquery_name, subquery in period_stats_queries.items()
        ]
    )
    for subquery in period_stats_queries.values():
        main_query = main_query.join(subquery, subquery.c.offer_id == Offer.id, isouter=True)

    if filter.offer_ids:
        main_query = main_query.where(Offer.id.in_(filter.offer_ids))

    result = (await session.execute(main_query)).all()
    stat_model_fields = {
        'offer_id': (int, ...)
    }
    stat_model_fields.update({i.field_name: (int, ...) for i in filter.periods})
    StatModel = create_model('OrdersStatistic', **stat_model_fields)
    return [StatModel.model_validate(i, from_attributes=True) for i in result]


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
    period_stats_queries = {
        period.field_name: _build_quantity_warehouses_query(period.field_name, period.days_interval, filter.offer_ids, filter.warehouse_ids)
        for period in filter.periods
    }

    main_query = select(
        OfferStock.offer_id.label('offer_id'),
        OfferStock.warehouse_id.label('warehouse_id'),
        *[
            func.coalesce(getattr(subquery.c, subquery_name), 0).label(subquery_name)
            for subquery_name, subquery in period_stats_queries.items()
        ]
    )
    for subquery in period_stats_queries.values():
        main_query = main_query.join(subquery, and_(subquery.c.offer_id == OfferStock.offer_id, subquery.c.warehouse_id == OfferStock.warehouse_id), isouter=True)

    if filter.offer_ids:
        main_query = main_query.where(OfferStock.offer_id.in_(filter.offer_ids))

    if filter.warehouse_ids:
        main_query = main_query.where(OfferStock.warehouse_id.in_(filter.warehouse_ids))

    result = (await session.execute(main_query)).all()
    stat_model_fields = {
        'offer_id': (int, ...),
        'warehouse_id': (int, ...),
    }
    stat_model_fields.update({i.field_name: (int, ...) for i in filter.periods})
    StatModel = create_model('OrdersStatistic', **stat_model_fields)
    return [StatModel.model_validate(i, from_attributes=True) for i in result]
