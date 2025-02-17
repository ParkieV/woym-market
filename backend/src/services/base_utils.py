import shutil
from functools import wraps
from io import BytesIO
from typing import Type
import numpy as np
import pandas as pd
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from starlette import status

from logs import backend_logger
from pathlib import Path



def error_handler(default_message: str = 'Ошибка сервера'):

    def wrapper(func):

        @wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                backend_logger.error(f'Error in func {func}: {e.detail}', exc_info=True)
                raise HTTPException(e.status_code, e.detail)

            except Exception:
                backend_logger.error(f'Error in func {func}', exc_info=True)
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
    except Exception:
        backend_logger.exception(f'Cannot remove file or dir \'{file_path}\'', exc_info=True)


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


def bytes_to_data_frame(data: bytes, sheet_name: str | int = 0, file_extension: str = '.xlsx', header: int = 0) -> pd.DataFrame:
    io = BytesIO(data)
    pd_engine = {
        '.xlsx': 'openpyxl',
        '.xls': 'xlrd'
    }
    if file_extension not in pd_engine.keys():
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f'Файлы с расширением "{file_extension}" не поддерживаются')

    return pd.read_excel(io, engine=pd_engine[file_extension], sheet_name=sheet_name, header=header)


def parce_field_names(cls: Type[BaseModel], reverse: bool = False, exclude: list[str] | None = None):
    if exclude is None:
        exclude = []
    fields = {key: value.title for key, value in cls.model_fields.items() if key not in exclude and value.title is not PydanticUndefined}

    if not reverse:
        return fields

    return {value: key for key, value in fields.items()}


def parce_sizes_list(data: bytes, file_extension: str = '.xlsx') -> pd.DataFrame:
    df = bytes_to_data_frame(data, 'Список товаров', file_extension)
    df.drop([0, 1], axis=0, inplace=True, errors='ignore')
    df: pd.DataFrame = df[df.columns[[2, 13, 14]]]
    df.columns = ['sku', 'yandex_weight', 'sizes']
    df[['yandex_length', 'yandex_width', 'yandex_height']] = df['sizes'].str.split('/', expand=True)
    df[['yandex_length', 'yandex_width', 'yandex_height', 'yandex_weight']] = df[
        ['yandex_length', 'yandex_width', 'yandex_height', 'yandex_weight']].astype(float)
    df['sku'] = df['sku'].astype('string')

    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    df.fillna(0, inplace=True)
    df.drop('sizes', axis=1, inplace=True)

    return df


def parce_purchase_list(data: bytes, file_extension: str = '.xlsx') -> pd.DataFrame:
    df = bytes_to_data_frame(data, file_extension=file_extension)
    df.drop(df.columns[[3, 4, 6, 7]], axis=1, inplace=True, errors='ignore')
    df.drop([i for i in range(8)], axis=0, inplace=True, errors='ignore')
    df.columns = ['sku', 'name', 'discount_price', 'price']

    df['sku'] = df['sku'].astype('string')

    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    df['use_promotion_price'] = df['discount_price'].notna()
    df['wholesale_dollar_cost_price'] = df['price']

    df['wholesale_dollar_cost_price'] = np.where(
        df['use_promotion_price'],
        df['discount_price'],
        df['wholesale_dollar_cost_price']
    )
    df.drop(['name', 'discount_price', 'price'], axis=1, inplace=True)
    df.dropna(axis='rows', inplace=True)
    return df





