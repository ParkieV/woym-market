from enum import Enum
from typing import Hashable, Callable
from .yandex_market.repository import YandexMarketRepository


class MPTypes(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yndx'


class RepositoryFactory:
    __classes: dict[Hashable, Callable[..., object]] = {
        MPTypes.YANDEX: YandexMarketRepository
    }

    @classmethod
    def get(cls, rep_type: MPTypes, *init_args, **init_kwargs):
        _class = cls.__classes.get(rep_type, None)
        if _class is None:
            raise KeyError(f'"{MPTypes}" Repository not in registry')

        try:
            instance = _class(*init_args, **init_kwargs)
        except TypeError as e:
            raise ValueError(f'Incorrect data to initialize class {rep_type} - "{_class}". Passed data: {init_args}, {init_kwargs}')

        return instance

