from fastapi import APIRouter, Depends
from src.schemas.settings_schemas import ColumnFullUpdate
from src.schemas.offer_schemas import OfferOut, OfferDelete
from src.services import offer_service, settings_service
from src.services.auth_utils import get_current_user

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


@debug_router.put('/columns')
async def full_update_columns(data: list[ColumnFullUpdate], current_user=Depends(get_current_user)):
    await settings_service.update_columns(current_user.id, data)
    return {'status': 'OK'}



