from enum import Enum
from typing import Hashable, Callable
from .yandex_market.repository import YandexMarketRepository
from .yandex_market.api import YandexMarketAPI
from src.params.confing import config
from .repositories import BaseRepository


class MPTypes(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yndx'


class RepositoryFactory:
    __classes: dict[Hashable, BaseRepository] = {
        MPTypes.YANDEX: YandexMarketRepository(
            YandexMarketAPI(config.yandex_token)
        )
    }

    @classmethod
    def get(cls, rep_type: MPTypes) -> BaseRepository:
        instance = cls.__classes.get(rep_type, None)
        if instance is None:
            raise KeyError(f'"{MPTypes}" Repository not in registry')

        return instance

