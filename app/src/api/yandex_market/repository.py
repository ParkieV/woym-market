from src.api.yandex_market.api import YandexMarketAPI
from src.api.repositories import BaseRepository


class YandexMarketRepository(BaseRepository):
    def __init__(self, api: YandexMarketAPI):
        self._api = api

    async def get_offers(self):
        return await self._api.get_offers()

    async def get_stocks(self, resp_type):
        #TODO написать логику
        pass

    async def change_prices(self, data):
        return self._api.change_offers_price(data)

