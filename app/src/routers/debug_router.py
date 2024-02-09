from fastapi import APIRouter, Depends
from src.schemas.offer_schemas import OfferDelete
from src.services import offer_service, settings_service
from src.services.auth_utils import get_current_user
from src.schemas.settings_schemas import ColumnCreate

debug_router = APIRouter(
    prefix='/debug',
    tags=['Debug']
)


@debug_router.delete('/offers', dependencies=[Depends(get_current_user)])
async def delete_offers(offers: list[OfferDelete]):
    await offer_service.delete_offers(offers)
    return {'status': 'OK'}


@debug_router.post('/offers/force-update')
async def force_update(current_user=Depends(get_current_user)):
    await offer_service.update_offers(current_user.id)
    return {'status': 'OK'}


@debug_router.post('/columns')
async def create_columns(data: list[ColumnCreate], current_user=Depends(get_current_user)):
    return await settings_service.create_columns(data, current_user.id)


@debug_router.delete('/columns')
async def delete_columns(data: list[int], current_user=Depends(get_current_user)):
    await settings_service.delete_columns(data, current_user.id)
    return {'status': 'OK'}


