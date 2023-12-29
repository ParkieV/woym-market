from fastapi import APIRouter, File, Depends
from fastapi.responses import FileResponse
from src.services.auth_utils import get_current_user
from src.schemas.offer_schemas import OfferOut, OfferChange, OfferDelete
from src.services import offer_service as service

offer_router = APIRouter(
    prefix='/offers',
    tags=['Offers']
)


@offer_router.get('/', response_model=list[OfferOut])
async def get_offers():
    return await service.get_offers()


@offer_router.patch('/', response_model=list[OfferOut])
async def change_offer_fields(offers_data: list[OfferChange], current_user=Depends(get_current_user)):
    return await service.change_offers(offers_data, current_user.id)


@offer_router.delete('/', dependencies=[Depends(get_current_user)])
async def delete_offers(offers: list[OfferDelete]):
    await service.delete_offers(offers)
    return {'status': 'OK'}


@offer_router.post('/send', dependencies=[Depends(get_current_user)])
async def send_offer_to_yandex():
    return await service.update_yandex_offers_price()


@offer_router.post('/setup', dependencies=[Depends(get_current_user)])
async def setup_offers_data():
    await service.setup_offers_data()
    return {'status': 'OK'}


@offer_router.get('/xlsx')
async def export_offers():
    path = await service.build_csv()
    return FileResponse(path=path, filename='out.xlsx', media_type='multipart/form-data')


@offer_router.get('/test_update', response_model=list[OfferOut])
async def test_update(current_user=Depends(get_current_user)):
    return await service.update_offers(current_user.id)


@offer_router.post('/xlsx')
async def import_offers(data: bytes = File(), current_user=Depends(get_current_user)):
    try:
        await service.import_offers_data(data, current_user.id)
    except Exception as e:
        return {'status': 'ERROR', 'detail':'Файл поврежден или имеет неподдерживаемый формат'}
    return {'status': 'OK'}


