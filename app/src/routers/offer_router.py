from fastapi import APIRouter, File, Depends, UploadFile, HTTPException, status
from fastapi.responses import FileResponse, Response

from src.services.auth_utils import get_current_user
from src.schemas.offer_schemas import OfferOut, OfferChange, OfferDelete, ImportType, ExportType, Market
from src.services import offer_service as service

offer_router = APIRouter(
    prefix='/offers',
    tags=['Offers']
)


@offer_router.get('', response_model=list[OfferOut])
async def get_offers():
    return await service.get_offers()


@offer_router.patch('', response_model=list[OfferOut])
async def change_offer_fields(offers_data: list[OfferChange], current_user=Depends(get_current_user)):
    return await service.change_offers(offers_data, current_user.id)


@offer_router.delete('', dependencies=[Depends(get_current_user)])
async def delete_offers(offers: list[OfferDelete]):
    await service.delete_offers(offers)
    return {'status': 'OK'}


@offer_router.post('/setup', dependencies=[Depends(get_current_user)])
async def setup_offers_data():
    await service.setup_offers_data()
    return {'status': 'OK'}


@offer_router.post('/force-update', response_model=list[OfferOut])
async def test_update(current_user=Depends(get_current_user)):
    return await service.update_offers(current_user.id)


@offer_router.get('/xlsx')
async def export_offers(market: Market = Market.YANDEX, export_type: ExportType = ExportType.TABLE, name_of_shop: str | None = None):
    path = await service.export_data(market, export_type, name_of_shop)
    return FileResponse(path=path, filename='out.xlsx', media_type='multipart/form-data')


@offer_router.post('/xlsx')
async def import_offers(data: UploadFile = File(), market: Market = Market.YANDEX, import_type: ImportType = ImportType.TABLE, name_of_shop: str | None = None, current_user=Depends(get_current_user)):
    if not data.filename.endswith('.xlsx'):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='Incorrect data type. Allowed only *.xlsx')

    content = await data.read()
    await service.import_data(content, market, import_type, name_of_shop, current_user.id)
    return {'status': 'OK'}







