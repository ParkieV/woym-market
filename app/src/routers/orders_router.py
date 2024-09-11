from fastapi import APIRouter, Depends, Body

from src.schemas.filters.filter_schemas import PagingFilter
from src.schemas.filters.orders_filter import OrderFilter
from src.schemas.filters.statistic_filter import OrderStatisticFilter
from src.schemas.orders_scemas import OrderOut, OrdersQuantityPeriodStatistic
from src.services import orders_services as service
from src.dependencies.users import get_current_user, require_staff

router = APIRouter(
    prefix="/orders",
    tags=['Заказы']
)


@router.post('', response_model=list[OrderOut], tags=['Debug'], dependencies=[Depends(get_current_user)], summary='Список заказов')
async def get_orders(filter: OrderFilter = Body(...), paging: PagingFilter = Body()):
    return await service.get_orders(filter, paging)


@router.delete('', dependencies=[Depends(require_staff)], summary='Удаление заказов из БД')
async def delete_orders(filter: OrderFilter = Body(...)):
    raise NotImplemented


@router.post('/statistic/only-offers', response_model=list[OrdersQuantityPeriodStatistic], dependencies=[Depends(get_current_user)], summary='Статистика заказов по товарам')
async def get_orders_statistic(filter: OrderStatisticFilter = Body(...)):
    return await service.get_orders_statistics_by_offers(filter)


@router.post('/statistic/offers-with-warehouses', response_model=list[OrdersQuantityPeriodStatistic], dependencies=[Depends(get_current_user)], summary='Статистика заказов по товарам со складов')
async def get_orders_statistic(filter: OrderStatisticFilter = Body(...)):
    return await service.get_order_statistics_by_offers_with_warehouses(filter)


@router.post('/setup', dependencies=[Depends(require_staff)])
async def setup_orders_data():
    await service.setup_orders()
    return {'status': 'OK'}




