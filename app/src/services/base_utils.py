import shutil
from functools import wraps
from fastapi.exceptions import HTTPException
from fastapi import status
from logs import get_logger
from pathlib import Path

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


def clean_up_files(file_path: str):
    try:
        path = Path(file_path)
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    except Exception as e:
        logger.exception(f'Cannot remove file or dir \'{file_path}\'', exc_info=True)
