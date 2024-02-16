from .base_api import BaseAPI
from src.schemas.base_api_schemas import APIWarehouse, APIOffer, APIPriceChangeData
from src.database.settings_db import get_markets
from src.api.factory import APIFactory
from ..database.db import async_session


class APIWrapper(BaseAPI):
    async def validate_auth_data(self, **kwargs):
        pass

    async def get_offers_list(self) -> list[APIOffer]:
        result = []
        async with async_session() as session:
            for market in await get_markets(session):
                api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                offers = await api.get_offers_list()
                result.extend(offers)

        return result

    async def get_stocks(self) -> list[APIWarehouse]:
        result = []
        async with async_session() as session:
            for market in await get_markets(session):
                api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                offers = await api.get_stocks()
                result.extend(offers)

        return result

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        async with async_session() as session:
            for market in await get_markets(session):
                api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)

                price_data = [i for i in data if i.market==market.type and i.name_of_shop==market.name]

                await api.change_prices(price_data)
