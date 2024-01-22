from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    async def get_offers(self):
        ...

    @abstractmethod
    async def get_stocks(self):
        ...

