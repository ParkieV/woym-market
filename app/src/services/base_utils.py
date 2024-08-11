import shutil
from functools import wraps
from typing import Type

import pandas as pd
from fastapi.exceptions import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic_core import PydanticUndefined

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


def validate_dataframe(
        df: pd.DataFrame,
        required_columns: list[str],
        full_entry: bool = True,
        allow_change: bool = False,
        raise_error: bool = True
) -> pd.DataFrame | None:
    df_columns = set(df.columns.to_list())

    if not len(required_columns):
        return df

    if full_entry:
        if set(required_columns) == df_columns:
            return df
    else:
        if set(required_columns).issubset(df_columns):
            if allow_change:
                return df[required_columns]
            else:
                return df

    if raise_error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'В файле должны присутствовать данные о количестве и SKU')

    return None


def parce_field_names(cls: Type[BaseModel], reverse: bool = False, exclude: list[str] | None = None):
    if exclude is None:
        exclude = []
    fields = {key: value.title for key, value in cls.model_fields.items() if key not in exclude and value.title is not PydanticUndefined}

    if not reverse:
        return fields

    return {value: key for key, value in fields.items()}



