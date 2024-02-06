from enum import Enum
from typing import Type
from .base_api import BaseAPI
from .yandex_market.api import YandexMarketAPI


class MPTypes(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yandex'


class APIFactory:
    __api_types: dict[MPTypes, Type[BaseAPI]] = {
        MPTypes.YANDEX: YandexMarketAPI
    }

    @classmethod
    def get(cls, api_type: MPTypes, **kwargs) -> BaseAPI:
        api_class = cls.__api_types.get(api_type, None)

        if api_class is None:
            raise ValueError(f'API class "{api_type}" not found in registered')

        try:
            api_instance = api_class(**kwargs)
        except TypeError:
            raise ValueError(f'Not enough arguments to inizialize "{api_type}"')

        return api_instance


