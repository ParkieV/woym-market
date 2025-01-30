import src.services.auth_utils as auth
from src.schemas.user_schemas import *
from src.services.settings_service import create_logs, create_settings
from src.services.auth_utils import hash_password
import src.database.user_db as user_db


async def registration_user(login: str, password: str, is_staff: bool):
    new_user = await auth.reg_user(login, password, is_staff)
    await create_settings(new_user.id)
    await create_logs(new_user.id)
    return new_user


async def login_user(login, password):
    user = await auth.auth_user(login, password)
    access_token = await auth.create_access_token({'user_id': user.id})

    user_data = {
        'access_token': access_token,
        'token_type': 'bearer'
    }

    return user_data


async def update_user_info(id_user: int, new_user_data: UserCreate):
    new_user_data.password = hash_password(new_user_data.password)
    await user_db.update_user(id_user, new_user_data)
