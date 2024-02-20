from fastapi import APIRouter, Depends
from src.services import stocks_service as service
from src.services.auth_utils import get_current_user
from src.schemas.stocks_schemas import OfferWithStocksUpdate, OfferWithStocks, OwnStorageUpdate, OwnStorages

stocks_router = APIRouter(
    prefix='/stocks',
    tags=['Stocks']
)


@stocks_router.get('/own-storage', dependencies=[Depends(get_current_user)], response_model=OwnStorages)
async def get_own_storages():
    return await service.get_own_storages()


@stocks_router.patch('/own-storage', dependencies=[Depends(get_current_user)])
async def change_own_storages(data: list[OwnStorageUpdate]):
    await service.change_own_storages(data)
    return {'status': 'OK'}


@stocks_router.get('/fbo', response_model=list[OfferWithStocks], dependencies=[Depends(get_current_user)])
async def get_fbo_stocks():
    return await service.get_offers_with_stocks()


@stocks_router.patch('/fbo', dependencies=[Depends(get_current_user)])
async def change_fbo_stocks(data: list[OfferWithStocksUpdate]):
    await service.change_offer_with_stock(data)
    return {'status': 'OK'}


@stocks_router.post('/setup', dependencies=[Depends(get_current_user)])
async def setup_fbo_stocks():
    await service.update_warehouses_and_stocks()
    return {'status': 'OK'}






