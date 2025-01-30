from fastapi import Depends, HTTPException
from starlette import status

from src.database import user_db as db
from src.database.models.models import Users
from src.params import auth as auth
from src.services.auth_utils import verify_access_token


async def get_current_user(token: str = Depends(auth.oauth2_scheme)) -> Users:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Не получилось авторизироваться в системе",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)

    user = await db.get_user_by_id(token.id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


async def require_staff(current_user = Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Действие доступно только персоналу')

    return current_user

