from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.services.user_service import *


auth_router = APIRouter(
    tags=['Авторизация'],
    prefix='/auth'
)


# @auth_router.post('/registration', response_model=UserOut, status_code=status.HTTP_201_CREATED)
# async def route_registration(user_reg: UserCreate):
#     new_user = await registration_user(user_reg.login, user_reg.password, user_reg.is_staff)
#     return new_user


@auth_router.post('/login', response_model=Token)
async def route_login(login_form: OAuth2PasswordRequestForm = Depends()):
    user_data = await login_user(login_form.username, login_form.password)
    return user_data

