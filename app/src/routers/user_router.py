from fastapi import APIRouter, status, Depends
from src.schemas.user_schemas import *
from src.services.user_service import *
from src.services.auth_utils import get_current_user

user_router = APIRouter(
    tags=['User'],
    prefix='/users'
)


@user_router.get('/settings', response_model=SettingsOut)
async def get_user_settings(current_user=Depends(get_current_user)):
    return await get_settings(current_user.id)


@user_router.patch('/settings')
async def update_settings(settings_data: SettingsUpdate, current_user=Depends(get_current_user)):
    await update_user_settings(current_user.id, settings_data)
    return {'status': 'OK'}


# TODO refactor this route
# @user_router.put('/')
# async def route_update_user(id_user: int, new_user_data: NewUserData, user = Depends(get_current_user)):
#     await update_user_info(id_user, new_user_data)
#     data = {
#         'msg': 'user successfully updated',
#         'id_user': id_user
#     }

#     return JSONResponse(data, status_code=status.HTTP_200_OK)
