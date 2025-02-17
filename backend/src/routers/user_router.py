from fastapi import APIRouter, Depends

from src.dependencies.users import get_current_user
from src.schemas.user_schemas import *
from src.services.user_service import update_user_info

user_router = APIRouter(
    tags=['Пользователи'],
    prefix='/users'
)


@user_router.get('/me', response_model=UserOut | None, summary='Текущий пользователь')
async def get_current_authorized_user(current_user=Depends(get_current_user)):
    if current_user is None:
        return current_user

    return UserOut.model_validate(current_user, from_attributes=True)


@user_router.patch('/')
async def route_update_user(id_user: int, new_user_data: UserCreate, user = Depends(get_current_user)):
    await update_user_info(id_user, new_user_data)
    data = {
        'msg': 'user successfully updated',
        'id_user': id_user
    }
    return data
