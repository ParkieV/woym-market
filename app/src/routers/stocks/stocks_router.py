from pathlib import Path

from fastapi import APIRouter, Depends, Body
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import get_current_user, require_staff
from src.routers.stocks.fbo_router import router as fbo_router
from src.routers.stocks.own_storage_router import router as own_storage_router
from src.schemas.stocks.warehouses_schemas import WarehouseOut
from src.services import stocks_service as service
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix="/stocks",
    tags=['Stocks']

)

router.include_router(fbo_router)
router.include_router(own_storage_router)


@router.get('/warehouses', response_model=list[WarehouseOut], tags=['Warehouses'], dependencies=[Depends(get_current_user)])
async def get_warehouses_list():
    return await service.get_warehouses()


@router.get('/warehouses/{warehouse_id}', response_model=WarehouseOut | None, tags=['Warehouses'], dependencies=[Depends(get_current_user)])
async def get_warehouse(warehouse_id: int):
    return await service.get_warehouse(warehouse_id)


@router.post('/setup', dependencies=[Depends(require_staff)])
async def setup_fbo_stocks():
    await service.update_warehouses_and_stocks()
    return {'status': 'OK'}


@router.post('/supply/export', dependencies=[Depends(require_staff)], tags=['Export'])
async def export_supply(warehouses_id: list[int] | None = Body(None), offers_id: list[int] | None = Body(None), market: str | None = Body(None), name_of_shop: str | None = Body(None)):
    path = Path(await service.export_supply(warehouses_id, offers_id, name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


