from os import getenv

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from src.params.config import config

SECRET_KEY = getenv('SECRET_KEY', 'SECRET')
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login' if config.is_local else '/backend/auth/login')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
