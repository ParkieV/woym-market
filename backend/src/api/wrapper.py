from dataclasses import asdict
from datetime import datetime

from logs import get_logger
from .base_api import BaseAPI
from src.schemas.base_api_schemas import APIWarehouse, APIOffer, APIPriceChangeData, APIOrderData, APIOfferChangeData
from src.database.settings_db import get_markets
from src.api.factory import APIFactory
from ..database.db import async_session
from src.schemas.settings_schemas import MarketFullOut


logger = get_logger(__name__, tags={'marketplace_api': 'api wrapper'})


class APIWrapper(BaseAPI):
    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        result = []
        async with async_session() as session:
            for market in await get_markets(session, MarketFullOut):
                api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                orders = await api.get_orders(from_date, to_date)

                if not orders:
                    logger.warning(f'Orders list for {market.name}({market.type}) is empty')

                result.extend(orders)
        return result

    async def validate_auth_data(self, **kwargs):
        pass

    async def get_offers_list(self) -> list[APIOffer]:
        result = []
        async with async_session() as session:
            for market in await get_markets(session, MarketFullOut):
                try:
                    api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                except Exception as e:
                    logger.error(f"Failed to get connect with Market. {e.__class__.__name__}: {e}")
                    continue

                offers = await api.get_offers_list()
                logger.info(f'{market.name}({market.type}) offers collected: {len(offers)}')
                if not offers:
                    logger.warning(f'{market.name}({market.type}) returns empty offers list')
                result.extend(offers)

        return result

    async def get_stocks(self) -> list[APIWarehouse]:
        result = []
        async with async_session() as session:
            for market in await get_markets(session, MarketFullOut):
                try:
                    api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                except Exception as e:
                    logger.error(f"Failed to get connect with Market. {e.__class__.__name__}: {e}")
                    continue
                offers = await api.get_stocks()
                logger.info(f'{market.name}({market.type}) offer stocks collected: {len(offers)}')
                if not offers:
                    logger.warning(f'{market.name}({market.type}) returns empty stocks list')
                result.extend(offers)

        return result

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        async with async_session() as session:
            for market in await get_markets(session, MarketFullOut):
                try:
                    api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                except Exception as e:
                    logger.error(f"Failed to get connect with Market. {e.__class__.__name__}: {e}")
                    continue

                price_data = [i for i in data if i.market==market.type and i.name_of_shop==market.name]

                try:
                    pass
                    # await api.change_prices(price_data)
                except Exception as e:
                    logger.error(f"Failed to change prices. {e.__class__.__name__}: {e}")
                    continue

    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        async with async_session() as session:
            for market in await get_markets(session, MarketFullOut):
                api = APIFactory.get(market.type, token=market.token, entity_id=market.entity_id, shop_name=market.name)
                offers_data = [i for i in data if i.market==market.type and i.name_of_shop==market.name]
                # await api.change_offers(offers_data)

