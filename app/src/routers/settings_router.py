from fastapi import Depends, APIRouter
from src.services import settings_service as service
from src.schemas.settings_schemas import LogsOut, SettingsOut, SettingsUpdate, TableInfoOut, TableInfoUpdate, Tables
from src.services.auth_utils import get_current_user

settings_router = APIRouter(
    prefix='/settings',
    tags=['Settings']
)


@settings_router.get('', response_model=SettingsOut)
async def get_settings(current_user=Depends(get_current_user)):
    return await service.get_settings(current_user.id)


@settings_router.patch('')
async def update_settings(data: SettingsUpdate, current_user=Depends(get_current_user)):
    await service.update_settings(current_user.id, data)
    return {'status': 'OK'}


@settings_router.get('/logs', response_model=LogsOut)
async def get_logs(current_user=Depends(get_current_user)):
    return await service.get_logs(current_user.id)


@settings_router.get('/tables/{table_name}', response_model=TableInfoOut | None)
async def get_table(table_name: str, current_user=Depends(get_current_user)):
    return await service.get_table(current_user.id, table_name)


@settings_router.put('/tables')
async def update_table(data: TableInfoUpdate, current_user=Depends(get_current_user)):
    await service.update_table(current_user.id, data)
    return {'status': 'OK'}

