from fastapi import Depends, APIRouter
from src.services import settings_service as service
from src.schemas.settings_schemas import LogsOut, SettingsOut, SettingsUpdate, ColumnOut, ColumnUpdate
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
    return await service.update_settings(current_user.id, data)


@settings_router.get('/logs', response_model=LogsOut)
async def get_logs(current_user=Depends(get_current_user)):
    return await service.get_logs(current_user.id)


@settings_router.get('/columns', response_model=list[ColumnOut])
async def get_columns(current_user=Depends(get_current_user)):
    settings = await service.get_settings(current_user.id)
    return settings.columns


@settings_router.patch('/columns')
async def update_columns(data: list[ColumnUpdate], current_user=Depends(get_current_user)):
    return await service.update_columns(current_user.id, data)

