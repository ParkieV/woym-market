from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
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
async def change_offer_fields(offers_data: list[OfferChange]):
    return await service.change_offers(offers_data)


@offer_router.delete('/')
async def delete_offers(offers: list[OfferDelete]):
    return await service.delete_offers(offers)


@offer_router.post('/setup')
async def setup_offers_data():
    return await service.setup_offers_data()


@offer_router.get('/csv')
async def export_offers():
    path = await service.build_csv()
    return FileResponse(path=path, filename='out.xlsx', media_type='multipart/form-data')


@offer_router.get('/test_update')
async def test_update():
    return await service.update_offers()


@offer_router.post('/csv')
async def import_offers(data: UploadFile):
    raise NotImplementedError()


