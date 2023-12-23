from fastapi import HTTPException, status
import requests

import src.database.user_db as db
import src.services.auth_utils as auth
from src.database.models.models import Users

async def registration_user(login: str, password: str):
    new_user = await auth.reg_user(login, password)
    return new_user


async def login_user(login, password):
    user = await auth.auth_user(login, password)
    access_token = await auth.create_access_token({'user_id': user.id})

    user_data = {
        'access_token': access_token,
        'token_type': 'bearer'
    }

    return user_data


# async def update_user_info(id_user: int, user_data: NewUserData):
#     await db.update_user(id_user, user_data)
#     return
