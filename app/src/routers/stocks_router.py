from pathlib import PurePath, Path

from fastapi import APIRouter, Depends, File, UploadFile, Body
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.services import stocks_service as service
from src.dependencies.users import get_current_user, require_staff
from src.schemas.stocks_schemas import OfferWithStocksUpdate, OfferWithStocks, OwnStorageUpdate, OwnStorages, \
    WarehouseOut, OwnStoragePlaceCreate, OwnStoragePlaceOut, OwnStoragePlaceUpdate
from src.services.base_utils import clean_up_files

stocks_router = APIRouter(
    prefix='/stocks',
    tags=['Stocks']
)



@stocks_router.post('/own-storage/places', dependencies=[Depends(require_staff)], tags=['Own storage', 'Own storage place'])
async def create_own_storage_places(data: list[OwnStoragePlaceCreate]):
    await service.create_own_storage_places(data)
    return {'status': 'OK'}


@stocks_router.patch('/own-storage/places', dependencies=[Depends(require_staff)], tags=['Own storage', 'Own storage place'])
async def change_own_storage_place(data: list[OwnStoragePlaceUpdate]):
    await service.change_own_storage_places(data)
    return {'status': 'OK'}


@stocks_router.get('/own-storage/places', dependencies=[Depends(get_current_user)], tags=['Own storage', 'Own storage place'])
async def get_own_storage_places():
    return await service.get_all_own_storage_places()


@stocks_router.get('/own-storage/{place_id}', dependencies=[Depends(get_current_user)], response_model=OwnStorages, tags=['Own storage'])
async def get_own_storages(place_id: int):
    return await service.get_own_storages(place_id)


@stocks_router.patch('/own-storage', dependencies=[Depends(require_staff)], tags=['Own storage'])
async def change_own_storages(data: list[OwnStorageUpdate]):
    await service.change_own_storages(data)
    return {'status': 'OK'}


@stocks_router.post('/own-storage/export', dependencies=[Depends(require_staff)], tags=['Own storage', 'Export'])
async def export_own_storage(place_id: int = Body(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    path = Path(await service.export_own_storages(place_id, name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@stocks_router.post('/own-storage/coming/import', dependencies=[Depends(require_staff)], tags=['Own storage', 'Import'])
async def import_own_storage_coming(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    pass


@stocks_router.post('/own-storage/consumption/import', dependencies=[Depends(require_staff)], tags=['Own storage', 'Import'])
async def import_own_storage_consumption(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    pass


@stocks_router.post('/own-storage/import', dependencies=[Depends(require_staff)], tags=['Own storage', 'Import'])
async def import_own_storage(data: UploadFile = File(), place_id: int = Body(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    content = await data.read()
    await service.import_own_storages(content, place_id, name_of_shop, market, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@stocks_router.get('/fbo', response_model=list[OfferWithStocks], dependencies=[Depends(get_current_user)], tags=['FBO'])
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





