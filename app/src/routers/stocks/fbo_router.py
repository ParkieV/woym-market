from pathlib import PurePath, Path

from fastapi import APIRouter, Depends, Body, UploadFile, File, HTTPException
from starlette import status
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import get_current_user, require_staff
from src.schemas.stocks.fbo_schemas import OfferWithFBOInfo, OfferWithFBOUpdate, OfferStockWithWarehouseOut, \
    OfferFBOStockUpdate
from src.services import stocks_service as service
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix='/fbo',
    tags=['FBO']
)


@router.post('/offers', response_model=list[OfferWithFBOInfo], dependencies=[Depends(get_current_user)])
async def get_fbo_offers(warehouses_id: list[int] | None = Body(default=None, embed=True)):
    return await service.get_fbo_offers(warehouses_id)


@router.patch('/offers', dependencies=[Depends(require_staff)])
async def change_offer(data: list[OfferWithFBOUpdate]):
    await service.change_fbo_offers(data)
    return {'status': 'OK'}


@router.get('/remains/{offer_id}', response_model=list[OfferStockWithWarehouseOut], dependencies=[Depends(get_current_user)])
async def get_fbo_stock(offer_id: int):
    return await service.get_offer_stocks(offer_id)


@router.patch('/remains', dependencies=[Depends(require_staff)])
async def change_offer_remain_stocks(data: list[OfferFBOStockUpdate]):
    await service.change_fbo_stocks(data)
    return {'status': 'OK'}


@router.post('/additions/import', dependencies=[Depends(require_staff)], tags=['Import'], description='Extended info about fbo stocks like a can_be_delivered, advice_from_the_store')
async def import_fbo_additions_data(data: UploadFile = File(), name_of_shop: str | None = Body(None), warehouse_id: int | None = Body(None)):
    content = await data.read()
    await service.import_fbo_data(content, name_of_shop, warehouse_id, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@router.post('/import',  dependencies=[Depends(require_staff)], tags=['Import'], deprecated=True)
async def import_fbo(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    raise HTTPException(status.HTTP_410_GONE, 'Данное действие больше недотупно. Обратитесь к администратору')


@router.post('/export', dependencies=[Depends(get_current_user)], tags=['Export'], deprecated=True)
async def export_fbo_stocks(name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    raise HTTPException(status.HTTP_410_GONE, 'Данное действие больше недотупно. Обратитесь к администратору')
