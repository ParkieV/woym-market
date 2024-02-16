from enum import Enum
from typing import Type
from .base_api import BaseAPI
from fastapi.exceptions import HTTPException
from fastapi import status
from .yandex_market.api import YandexMarketAPI


class APITypes(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yandex'


class APIFactory:
    __api_types: dict[APITypes, Type[BaseAPI]] = {
        APITypes.YANDEX: YandexMarketAPI
    }

    @classmethod
    def get(cls, api_type: APITypes, **kwargs) -> BaseAPI:
        api_class = cls.__api_types.get(api_type, None)

        if api_class is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'API class \"{api_type}\" not found in registered')

        try:
            api_instance = api_class(**kwargs)
        except TypeError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Not enough arguments to inizialize \"{api_type}\"')

        return api_instance


