from pathlib import PurePath

from fastapi import APIRouter, Depends, File, UploadFile
from src.services import stocks_service as service
from src.dependencies.users import get_current_user, require_staff
from src.schemas.stocks_schemas import OfferWithStocksUpdate, OfferWithStocks, OwnStorageUpdate, OwnStorages, \
    WarehouseOut

stocks_router = APIRouter(
    prefix='/stocks',
    tags=['Stocks']
)


@stocks_router.get('/own-storage', dependencies=[Depends(get_current_user)], response_model=OwnStorages)
async def get_own_storages():
    return await service.get_own_storages()


@stocks_router.patch('/own-storage', dependencies=[Depends(require_staff)])
async def change_own_storages(data: list[OwnStorageUpdate]):
    await service.change_own_storages(data)
    return {'status': 'OK'}


@stocks_router.get('/fbo', response_model=list[OfferWithStocks], dependencies=[Depends(get_current_user)])
async def get_fbo_stocks():
    return await service.get_offers_with_stocks()


@stocks_router.patch('/fbo', dependencies=[Depends(require_staff)])
async def change_fbo_stocks(data: list[OfferWithStocksUpdate]):
    await service.change_offer_with_stock(data)
    return {'status': 'OK'}


@stocks_router.get('/warehouses', response_model=list[WarehouseOut])
async def get_warehouses():
    return await service.get_warehouses()


@stocks_router.post('/setup', dependencies=[Depends(require_staff)])
async def setup_fbo_stocks():
    await service.update_warehouses_and_stocks()
    return {'status': 'OK'}


@stocks_router.post('/fbo/import', dependencies=[Depends(require_staff)])
async def import_fbo_data(data: UploadFile = File(), name_of_shop: str | None = None, warehouse_id: int | None = None):
    content = await data.read()

    await service.import_fbo_data(content, name_of_shop, warehouse_id, PurePath(data.filename).suffix)


@stocks_router.get('/fbo/import/choices', dependencies=[Depends(require_staff)])
async def get_choices_for_import_fbo_data():
    return await service.get_choices_for_import_fbo_data()





