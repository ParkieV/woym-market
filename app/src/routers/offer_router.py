from fastapi import APIRouter, UploadFile
from src.schemas.offer_schemas import OfferOut, OfferChange
from src.services import offer_service as service

offer_router = APIRouter(
    prefix='/offers',
    tags=['Offers']
)


@offer_router.get('/', response_model=list[OfferOut])
async def get_offers(limit: int = 600, offset: int = 0):
    return await service.get_offers(limit, offset)


@offer_router.post('/change')
async def change_offer_fields(offers_data: list[OfferChange]):
    raise NotImplementedError()


@offer_router.post('/setup')
async def setup_offers_data():
    return await service.setup_offers_data()


@offer_router.get('/export')
async def export_offers():
    raise NotImplementedError()


@offer_router.post('/import')
async def import_offers(data: UploadFile):
    raise NotImplementedError()


