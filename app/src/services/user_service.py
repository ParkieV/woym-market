import src.services.auth_utils as auth
from src.services.settings_service import create_logs, create_settings


async def registration_user(login: str, password: str, is_staff: bool):
    new_user = await auth.reg_user(login, password, is_staff)
    settings = await create_settings(new_user.id)
    logs = await create_logs(new_user.id)
    return new_user


async def login_user(login, password):
    user = await auth.auth_user(login, password)
    access_token = await auth.create_access_token({'user_id': user.id})

    user_data = {
        'access_token': access_token,
        'token_type': 'bearer'
    }

    return user_data

