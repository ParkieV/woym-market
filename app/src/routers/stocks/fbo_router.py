from pathlib import PurePath, Path

from fastapi import APIRouter, Depends, Body, UploadFile, File
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import get_current_user, require_staff
from src.schemas.stocks.fbo_schemas import OfferWithStocks, OfferWithStocksUpdate, OfferStockWithWarehouseOut
from src.services import stocks_service as service
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix='/fbo',
    tags=['FBO']
)


@router.get('', response_model=list[OfferWithStocks], dependencies=[Depends(get_current_user)])
async def get_fbo_offers():
    return await service.get_fbo_offers()


@router.get('/{offer_id}', response_model=list[OfferStockWithWarehouseOut], dependencies=[Depends(get_current_user)])
async def get_fbo_stock(offer_id: int):
    return await service.get_offer_stock(offer_id)


@router.patch('', dependencies=[Depends(require_staff)])
async def change_fbo_stocks(data: list[OfferWithStocksUpdate]):
    await service.change_offer_with_stock(data)
    return {'status': 'OK'}


@router.post('/additions/import', dependencies=[Depends(require_staff)], tags=['Import'], description='Extended info about fbo stocks like a can_be_delivered, advice_from_the_store')
async def import_fbo_additions_data(data: UploadFile = File(), name_of_shop: str | None = Body(None), warehouse_id: int | None = Body(None)):
    content = await data.read()
    await service.import_fbo_data(content, name_of_shop, warehouse_id, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@router.post('/import',  dependencies=[Depends(require_staff)], tags=['Import'])
async def import_fbo(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    content = await data.read()
    await service.import_offers_stocks(content, name_of_shop, market, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@router.post('/export', dependencies=[Depends(require_staff)], tags=['Export'])
async def export_fbo_stocks(name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    path = Path(await service.export_stocks(name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))