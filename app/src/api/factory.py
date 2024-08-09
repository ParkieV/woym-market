from enum import Enum
from typing import Type
from .base_api import BaseAPI
from fastapi.exceptions import HTTPException
from fastapi import status
from .yandex_market.api import YandexMarketAPI
from .ozon.api import OzonAPI
from .wildberries.api import WildberriesAPI


class APITypes(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yandex'
    WILDBERRIES = 'wildberries'


class APIFactory:
    __api_types: dict[APITypes, Type[BaseAPI]] = {
        APITypes.YANDEX: YandexMarketAPI,
        APITypes.OZON: OzonAPI,
        APITypes.WILDBERRIES: WildberriesAPI
    }

    @classmethod
    def get(cls, api_type: APITypes, **kwargs) -> BaseAPI:
        api_class = cls.__api_types.get(api_type, None)

        if api_class is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'API \"{api_type}\"  не найдено в зарегестрированных')

        try:
            api_instance = api_class(**kwargs)
        except TypeError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Недостаточно аргументов или неверные аргументы, чтобы инициализировать API \"{api_type}\"')

        return api_instance


