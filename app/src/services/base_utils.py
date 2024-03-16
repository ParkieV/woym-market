from functools import wraps
from fastapi.exceptions import HTTPException
from fastapi import status
from logs import get_logger

logger = get_logger(__name__)


def error_handler(default_message: str = 'Ошибка сервера'):

    def wrapper(func):

        @wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                logger.error(f'Error in func {func}: {e.detail}', exc_info=True)
                raise HTTPException(e.status_code, e.detail)

            except Exception as e:
                logger.error(f'Error in func {func}', exc_info=True)
                raise HTTPException(status.HTTP_400_BAD_REQUEST, default_message)

        return wrapped

    return wrapper
