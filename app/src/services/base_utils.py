from functools import wraps

from fastapi.exceptions import HTTPException
from fastapi import status


def error_handler(default_message: str = 'Ошибка сервера'):

    def wrapper(func):

        @wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                print(func)
                print(e)
                raise HTTPException(e.status_code, e.detail)

            except Exception as e:
                print(e)
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, default_message)

        return wrapped

    return wrapper

