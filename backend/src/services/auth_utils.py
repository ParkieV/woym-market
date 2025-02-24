from datetime import datetime, timedelta

from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import HTTPException, status

# from database.admins_db import get_admin_by_email
import src.params.auth as auth
import src.database.user_db as db
from src.database.models.models import Users
from src.schemas.user_schemas import TokenData


def hash_password(password: str) -> str:
    return auth.pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return auth.pwd_context.verify(plain_password, hashed_password)


async def reg_user(login: str, password: str, is_staff: bool):
    pass_hash = hash_password(password)
    new_user = await db.reg_user(login, pass_hash, is_staff)
    return new_user


async def auth_user(login: str, password: str) -> Users:
    user = await db.get_user_by_login(login)
    if not user:
        raise HTTPException(
            detail='Неверный логин или пароль.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            detail='Неверный логин или пароль.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return user


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        id = payload.get("user_id")

        if id is None:
            raise credentials_exception

        now = datetime.now()
        exp = datetime.fromtimestamp(payload.get('exp'))

        if now > exp:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Время сессии истекло.')

        token_data = TokenData(id=str(id))

    except ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Время сессии истекло.')

    except JWTError:
        raise credentials_exception

    return token_data
