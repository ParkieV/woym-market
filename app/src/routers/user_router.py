from fastapi import APIRouter, status, Depends
from src.schemas.user_schemas import *
from src.services.user_service import *
from src.dependencies.users import get_current_user

user_router = APIRouter(
    tags=['User'],
    prefix='/users'
)


@user_router.get('/me', response_model=UserOut | None)
async def get_current_authorized_user(current_user=Depends(get_current_user)):
    if current_user is None:
        return current_user

    return UserOut.model_validate(current_user, from_attributes=True)


# TODO refactor this route
# @user_router.put('/')
# async def route_update_user(id_user: int, new_user_data: NewUserData, user = Depends(get_current_user)):
#     await update_user_info(id_user, new_user_data)
#     data = {
#         'msg': 'user successfully updated',
#         'id_user': id_user
#     }

#     return JSONResponse(data, status_code=status.HTTP_200_OK)
