from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from src.schemas.user_schemas import *
from src.services.user_service import *
from src.services.auth_utils import get_current_user
from requests import post
import json

user_router = APIRouter(
    tags=['User'],
    prefix='/users'
)


@user_router.get('/hello')
async def route_get_user(data: str):
    return {'msg': f'Hello {data}!'}


@user_router.get('/me',  response_model=UserOut)
async def route_get_user(current_user: dict = Depends(get_current_user)):
    return current_user


# TODO refactor this route
# @user_router.put('/')
# async def route_update_user(id_user: int, new_user_data: NewUserData, user = Depends(get_current_user)):
#     await update_user_info(id_user, new_user_data)
#     data = {
#         'msg': 'user successfully updated',
#         'id_user': id_user
#     }

#     return JSONResponse(data, status_code=status.HTTP_200_OK)
