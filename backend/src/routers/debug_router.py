from fastapi import APIRouter, Depends, BackgroundTasks

from src.database.db import get_db_session
from src.schemas.offer_schemas import OfferDelete
from src.services import offer_service, settings_service
from src.dependencies.users import require_staff
from src.schemas.settings_schemas import MarketFullUpdate

debug_router = APIRouter(
    prefix='/debug',
    tags=['Debug']
)


@debug_router.delete('/offers', dependencies=[Depends(require_staff)])
async def delete_offers(offers: list[OfferDelete]):
    await offer_service.delete_offers(offers)
    return {'status': 'OK'}


@debug_router.post('/offers/force-update')
async def force_update(background: BackgroundTasks, current_user=Depends(require_staff)):
    background.add_task(offer_service.update_offers, get_db_session, current_user.id)
    # await offer_service.update_offers(current_user.id)
    return {'status': 'OK'}


@debug_router.patch('/settings/markets')
async def create_market(data: MarketFullUpdate, current_user=Depends(require_staff)) -> None:
    await settings_service.change_market(data.id, data, current_user.id)
