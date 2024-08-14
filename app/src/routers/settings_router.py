from fastapi import Depends, APIRouter

from src.dependencies.users import get_current_user, require_staff
from src.schemas.settings_schemas import LogsOut, SettingsOut, SettingsUpdate, TableInfoOut, TableInfoUpdate, MarketOut, \
    MarketCreate, MarketUpdate, TableInfoCreate
from src.services import settings_service as service

settings_router = APIRouter(
    prefix='/settings',
    tags=['Settings']
)


@settings_router.get('', response_model=SettingsOut)
async def get_settings(current_user=Depends(get_current_user)):
    return await service.get_settings(current_user.id)


@settings_router.patch('')
async def update_settings(data: SettingsUpdate, current_user=Depends(require_staff)):
    await service.update_settings(current_user.id, data)
    return {'status': 'OK'}


@settings_router.get('/logs', response_model=LogsOut)
async def get_logs(current_user=Depends(get_current_user)):
    return await service.get_logs(current_user.id)


@settings_router.get('/tables/{table_name}', response_model=TableInfoOut | None, dependencies=[Depends(get_current_user)])
async def get_table(table_name: str):
    return await service.get_table(table_name)


@settings_router.put('/tables', dependencies=[Depends(require_staff)])
async def update_or_create_table(data: TableInfoUpdate):
    await service.update_or_create_table(data)
    return {'status': 'OK'}


@settings_router.post('/tables', dependencies=[Depends(require_staff)])
async def create_table(data: TableInfoCreate):
    await service.create_table(data)
    return {'status': 'OK'}


@settings_router.patch('/tables/{table_name}')
async def update_table(data: TableInfoUpdate, table_name: str,  current_user=Depends(require_staff)):
    await service.update_table(current_user.id, table_name, data)
    return {'status': 'OK'}


@settings_router.get('/markets', response_model=list[MarketOut], dependencies=[Depends(get_current_user)])
async def get_markets():
    return await service.get_markets()


@settings_router.post('/markets', response_model=MarketOut, dependencies=[Depends(require_staff)])
async def create_market(data: MarketCreate):
    return await service.create_market(data)


@settings_router.patch('/markets/{market_id}', dependencies=[])
async def change_market(market_id: int, data: MarketUpdate, current_user=Depends(require_staff)):
    await service.change_market(market_id, data, current_user.id)
    return {'status': 'OK'}


@settings_router.delete('/markets/{market_id}', dependencies=[Depends(require_staff)])
async def delete_market(market_id: int):
    await service.delete_market(market_id)
    return {'status': 'OK'}

