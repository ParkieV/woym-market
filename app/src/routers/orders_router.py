from fastapi import APIRouter, Depends, Body

from src.schemas.filters.orders_filter import OrderFilter
from src.schemas.filters.statistic_filter import OrderStatisticFilter
from src.schemas.orders_scemas import OrderOut, OrdersQuantityPeriodStatistic
from src.services import orders_services as service
from src.dependencies.users import get_current_user, require_staff

router = APIRouter(
    prefix="/orders",
    tags=['Заказы']
)


@router.post('', response_model=list[OrderOut], dependencies=[Depends(get_current_user)])
async def get_orders(filter: OrderFilter = Body(...)):
    return await service.get_orders(filter)


@router.delete('', dependencies=[Depends(require_staff)])
async def delete_orders(filter: OrderFilter = Body(...)):
    pass


@router.post('/statistic', response_model=list[OrdersQuantityPeriodStatistic], dependencies=[Depends(get_current_user)])
async def get_orders_statistic(filter: OrderStatisticFilter = Body(...)):
    return await service.get_order_statistics(filter)


@router.post('/statistic/setup', dependencies=[Depends(require_staff)])
async def setup_orders_data():
    await service.setup_orders()
    return {'status': 'OK'}




