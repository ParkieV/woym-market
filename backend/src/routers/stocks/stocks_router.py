from pathlib import Path

from fastapi import APIRouter, Depends, Body, BackgroundTasks
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import get_current_user, require_staff
from src.routers.stocks.fbo_router import router as fbo_router
from src.routers.stocks.own_storage_router import router as own_storage_router
from src.schemas.filters.stocks_filter import WarehousesFilter
from src.schemas.stocks.stocks_schemas import SupplyExportType
from src.schemas.stocks.warehouses_schemas import WarehouseOut
from src.services import stocks_service as service
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix="/stocks",
    tags=['Модуль остатков']

)

router.include_router(fbo_router)
router.include_router(own_storage_router)


@router.post('/warehouses', response_model=list[WarehouseOut], tags=['Склады маркетплейсов'], dependencies=[Depends(get_current_user)], summary='Список складов маркетплейсов')
async def get_warehouses_list(filter: WarehousesFilter | None = Body(None)):
    return await service.get_warehouses(filter)


@router.get('/warehouses/{warehouse_id}', response_model=WarehouseOut | None, tags=['Склады маркетплейсов'], dependencies=[Depends(get_current_user)], summary='Информация о складе маркетплейса')
async def get_warehouse(warehouse_id: int):
    return await service.get_warehouse(warehouse_id)


@router.post('/setup', dependencies=[Depends(require_staff)])
async def setup_fbo_stocks(background: BackgroundTasks):
    background.add_task(service.update_warehouses_and_stocks)
    return {'status': 'OK'}


@router.post('/supply/only-own-storage/export', tags=['Поставка', 'Экспорт'], dependencies=[Depends(get_current_user)], summary='Поставка Только Мой склад')
async def export_only_own_storage_supply(
        place_id: int = Body(title='ID склада продавца'),
        warehouses_id: list[int] = Body(title='ID складов маркетплейсов'),
        offers_id: list[int] = Body(title='ID карточек товаров')
):
    path = Path(await service.export_supply(SupplyExportType.ONLY_OWN_STORAGE, warehouses_id, offers_id, place_id=place_id))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@router.post('/supply/only-stocks/export', tags=['Поставка', 'Экспорт'], dependencies=[Depends(get_current_user)], summary='Поставка Без учета моих складов')
async def export_only_stocks_supply(
        warehouses_id: list[int] = Body(title='ID складов маркетплейсов'),
        offers_id: list[int] = Body(title='ID карточек товаров'),
):
    path = Path(await service.export_supply(SupplyExportType.ONLY_STOCKS, warehouses_id, offers_id))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data',
                        background=BackgroundTask(clean_up_files, str(path)))


@router.post('/supply/with-own-storage/export', tags=['Поставка', 'Экспорт'], dependencies=[Depends(get_current_user)], description='Поставка C учетом Мой склад')
async def export_with_own_storage_supply(
        place_id: int = Body(title='ID склада продавца'),
        warehouses_id: list[int] = Body(title='ID складов маркетплейсов'),
        offers_id: list[int] = Body(title='ID карточек товаров')
):
    path = Path(await service.export_supply(SupplyExportType.WITH_OWN_STORAGE, warehouses_id, offers_id, place_id=place_id))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data',
                        background=BackgroundTask(clean_up_files, str(path)))
