from fastapi import APIRouter, Depends

from src.services.auth_utils import get_current_user

stocks_router = APIRouter(
    prefix='/stocks',
    tags=['Stocks']
)


@stocks_router.get('/warehouses', dependencies=[Depends(get_current_user)])
async def get_warehouses():
    pass


@stocks_router.patch('/warehouses', dependencies=[Depends(get_current_user)])
async def change_warehouses(data: list):
    pass


@stocks_router.get('/offers', dependencies=[Depends(get_current_user)])
async def get_offers_stocks():
    pass


@stocks_router.patch('/offers', dependencies=[Depends(get_current_user)])
async def change_offers_stocks(data: list):
    pass


@stocks_router.post('/setup', dependencies=[Depends(get_current_user)])
async def setup_stocks():
    pass


