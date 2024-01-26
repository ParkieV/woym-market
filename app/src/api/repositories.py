from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    async def get_offers(self):
        pass

    @abstractmethod
    async def get_stocks(self, resp_type):
        pass

    @abstractmethod
    async def change_prices(self, data):
        pass

