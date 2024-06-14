import shutil
from functools import wraps
from typing import Callable
from fastapi.exceptions import HTTPException
from fastapi import status
from logs import get_logger
from pathlib import Path
from inspect import signature, Signature

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


class HandlersFactory:

    def __init__(self, name: str | None = None):
        self.name = name
        self.__handlers = {}

    def register(self, ident: str):
        def wrapper(func: Callable):
            if ident in self.__handlers.keys():
                raise ValueError(f"Ident {ident} already registered")

            self.__handlers[ident] = func
            return func

        return wrapper

    def unregister(self, ident: str):
        if ident in self.__handlers.keys():
            del self.__handlers[ident]

    def get(self, ident: str) -> Callable:
        if ident not in self.__handlers.keys():
            raise ValueError(f"Ident {ident} not registered")
        return self.__handlers[ident]

    async def __call__(self, ident: str, **kwargs):
        handler = self.get(ident)
        sig = signature(handler)

        params = {}
        for param_name in sig.parameters:
            if param_name not in kwargs:
                raise ValueError(f'Parameter {param_name} is required')

            # if not isinstance(kwargs[param_name], sig.parameters[param_name].annotation) and sig.parameters[param_name].annotation is not Signature.empty:
            #     raise TypeError

            params[param_name] = kwargs[param_name]

        return await handler(**params)

    def __repr__(self):
        if self.name:
            return f'Factory "{self.name}"'
        return super().__repr__()


import_handler_factory = HandlersFactory()
export_handler_factory = HandlersFactory()

