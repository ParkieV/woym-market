from pathlib import PurePath, Path

from fastapi import APIRouter, Depends, File, UploadFile, Body, BackgroundTasks
from fastapi_cache.decorator import cache
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.services import stocks_service as service
from src.dependencies.users import get_current_user, require_staff
from src.schemas.stocks_schemas import OfferWithStocksUpdate, OfferWithStocks, OwnStorageUpdate, OwnStorages, \
    WarehouseOut
from src.services.base_utils import clean_up_files

stocks_router = APIRouter(
    prefix='/stocks',
    tags=['Stocks']
)


@stocks_router.get('/own-storage', dependencies=[Depends(get_current_user)], response_model=OwnStorages, tags=['Own storage'])
async def get_own_storages():
    return await service.get_own_storages()


@stocks_router.patch('/own-storage', dependencies=[Depends(require_staff)], tags=['Own storage'])
async def change_own_storages(data: list[OwnStorageUpdate]):
    await service.change_own_storages(data)
    return {'status': 'OK'}


@stocks_router.post('/own-storage/setup', tags=['Own storage'])
async def set_up_own_storages(background: BackgroundTasks):
    background.add_task(service.create_own_storages)
    return {'status': 'OK'}


@stocks_router.post('/own-storage/export', dependencies=[Depends(require_staff)], tags=['Own storage', 'Export'])
async def export_own_storage(name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    path = Path(await service.export_own_storages(name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@stocks_router.post('/own-storage/import', dependencies=[Depends(require_staff)], tags=['Own storage', 'Import'])
async def import_own_storage(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    content = await data.read()
    await service.import_own_storages(content, name_of_shop, market, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@stocks_router.get('/fbo', response_model=list[OfferWithStocks], dependencies=[Depends(get_current_user)], tags=['FBO'])
@cache(60*5)
async def get_fbo_stocks():
    return await service.get_offers_with_stocks()


@stocks_router.patch('/fbo', dependencies=[Depends(require_staff)], tags=['FBO'])
async def change_fbo_stocks(data: list[OfferWithStocksUpdate]):
    await service.change_offer_with_stock(data)
    return {'status': 'OK'}


@stocks_router.get('/warehouses', response_model=list[WarehouseOut], tags=['Warehouses'], dependencies=[Depends(get_current_user)])
async def get_warehouses_list():
    return await service.get_warehouses()


@stocks_router.get('/warehouses/{warehouse_id}', response_model=WarehouseOut | None, tags=['Warehouses'], dependencies=[Depends(get_current_user)])
async def get_warehouse(warehouse_id: int):
    return await service.get_warehouse(warehouse_id)


@stocks_router.post('/setup', dependencies=[Depends(require_staff)])
async def setup_fbo_stocks():
    await service.update_warehouses_and_stocks()
    return {'status': 'OK'}


@stocks_router.post('/fbo/additions/import', dependencies=[Depends(require_staff)], tags=['FBO', 'Import'])
async def import_fbo_additions_data(data: UploadFile = File(), name_of_shop: str | None = Body(None), warehouse_id: int | None = Body(None)):
    content = await data.read()
    await service.import_fbo_data(content, name_of_shop, warehouse_id, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@stocks_router.post('/fbo/import',  dependencies=[Depends(require_staff)], tags=['FBO', 'Import'])
async def import_fbo(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    content = await data.read()
    await service.import_offers_stocks(content, name_of_shop, market, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@stocks_router.post('/fbo/export', dependencies=[Depends(require_staff)], tags=['FBO', 'Export'])
async def export_fbo_stocks(name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    path = Path(await service.export_stocks(name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))



@stocks_router.post('/supply/export', dependencies=[Depends(require_staff)], tags=['Export'])
async def export_supply(warehouses_id: list[int] | None = Body(None), offers_id: list[int] | None = Body(None), market: str | None = Body(None), name_of_shop: str | None = Body(None)):
    path = Path(await service.export_supply(warehouses_id, offers_id, name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))





