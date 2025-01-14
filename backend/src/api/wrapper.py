from datetime import datetime
from typing import Any

from logs import get_logger
from src.api.interfaces import IApiSessionFabric, ApiTypes
from src.database.interfaces import IDbSessionFabric
from src.schemas.base_api_schemas import APIWarehouse, APIPriceChangeData, APIOrderData, APIOfferChangeData
from src.database.settings_db import get_markets
from src.api.factory import ApiFactory
from src.database.db import async_session
from src.schemas.settings_schemas import MarketFullOut


logger = get_logger(__name__, tags={'marketplace_api': 'api wrapper'})


class ApiInteractor:

    def __init__(self, api_session_fabric: IApiSessionFabric, db_session_fabric: IDbSessionFabric):
        self.api_session_fabric = api_session_fabric
        self.db_session_fabric = db_session_fabric

    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        result = []
        api_factory = ApiFactory()
        async with self.db_session_fabric() as db_session:
            markets = await get_markets(db_session, MarketFullOut)

        for market in markets:
            async with self.api_session_fabric() as api_session:
                api = api_factory(market.type,
                    session=api_session,
                    token=market.token,
                    entity_id=str(market.entity_id) if market.entity_id else None,
                    shop_name=market.name)
                orders = await api.get_orders(from_date, to_date)

                if not orders:
                    logger.warning(f'Orders list for {market.name}({market.type}) is empty')

                result.extend(orders)
        return result

    async def get_offers_list(self) -> list[dict[str, Any]]:
        result = []
        api_factory = ApiFactory()
        async with self.db_session_fabric() as session:
            markets = await get_markets(session, MarketFullOut)

        for market in markets:
            async with self.api_session_fabric() as api_session:
                api = api_factory(market.type,
                    session=api_session,
                    token=market.token,
                    entity_id=str(market.entity_id) if market.entity_id else None,
                    shop_name=market.name)
                offers = await api.get_offers_list()
                logger.info(f'{market.name}({market.type}) offers collected: {len(offers)}')
                if not offers:
                    logger.warning(f'{market.name}({market.type}) returns empty offers list')
                result.extend([dict(_) for _ in offers])

        return result

    async def get_stocks(self) -> list[APIWarehouse]:
        result = []
        api_factory = ApiFactory()
        async with self.db_session_fabric() as db_session:
            markets = await get_markets(db_session, MarketFullOut)

        for market in markets:
            async with self.api_session_fabric() as api_session:
                try:
                    api = api_factory(market.type,
                        session=api_session,
                        token=market.token,
                        entity_id=str(market.entity_id) if market.entity_id else None,
                        shop_name=market.name)
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
        api_factory = ApiFactory()
        async with async_session() as session:
            for market in await get_markets(session, MarketFullOut):
                if market.type == 'ozon':
                    logger.debug('For debug')
                try:
                    api = api_factory(market.type,
                        session=session,
                        token=market.token,
                        entity_id=str(market.entity_id) if market.entity_id else None,
                        shop_name=market.name)
                except Exception as e:
                    logger.error(f"Failed to get connect with Market. {e.__class__.__name__}: {e}")
                    continue

                price_data = [i for i in data if i.market==market.type and i.name_of_shop==market.name]

                try:
                    await api.change_prices(price_data)
                except Exception as e:
                    logger.error(f"Failed to change prices. {e.__class__.__name__}: {e}")
                    continue

    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        api_factory = ApiFactory()
        async with self.db_session_fabric() as db_session:
            markets = await get_markets(db_session, MarketFullOut)

        for market in markets:
            async with self.api_session_fabric() as api_session:
                api = api_factory(market.type,
                    session=api_session,
                    token=market.token,
                    entity_id=str(market.entity_id) if market.entity_id else None,
                    shop_name=market.name)
                offers_data = [i for i in data if i.market==market.type and i.name_of_shop==market.name]
                await api.change_offers(offers_data)

