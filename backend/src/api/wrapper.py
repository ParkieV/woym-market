from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from dataclasses import dataclass

from sqlalchemy import text

from logs import parser_logger
from src.api.gateway_template import get_api_session
from src.api.interfaces import IApiSessionFabric
from src.database.catalog import CatalogRepository
from src.database.interfaces import IDbSessionFabric
from src.schemas.base_api_schemas import APIWarehouse, APIPriceChangeData, APIOrderData, APIOfferChangeData
from src.database.settings_db import get_markets
from src.api.factory import ApiFactory
from src.database.db import get_db_session
from src.schemas.settings_schemas import MarketFullOut



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
                    parser_logger.warning(f'Orders list for {market.name}({market.type}) is empty')

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
                parser_logger.info(f'{market.name}({market.type}) offers collected: {len(offers)}')
                if not offers:
                    parser_logger.warning(f'{market.name}({market.type}) returns empty offers list')
                result.extend((offer.model_dump() for offer in offers))

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
                    parser_logger.error(f"Failed to get connect with Market. {e.__class__.__name__}: {e}")
                    continue
                offers = await api.get_stocks()
                parser_logger.info(f'{market.name}({market.type}) offer stocks collected: {len(offers)}')
                if not offers:
                    parser_logger.warning(f'{market.name}({market.type}) returns empty stocks list')
                result.extend(offers)

        return result

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        api_factory = ApiFactory()
        async with self.db_session_fabric() as db_session:
            markets = await get_markets(db_session, MarketFullOut)
        async with self.api_session_fabric() as api_session:
            for market in markets:
                try:
                    api = api_factory(market.type,
                        session=api_session,
                        token=market.token,
                        entity_id=str(market.entity_id) if market.entity_id else None,
                        shop_name=market.name)
                except Exception as e:
                    parser_logger.error(f"Failed to get connect with {market.type}({market.name}). {e.__class__.__name__}: {e}")
                    continue

                price_data = [i for i in data if i.market==market.type and i.name_of_shop==market.name]

                try:
                    parser_logger.info(f'{market.name}({market.type}) offers length: {len(price_data)}')
                    await api.change_prices(price_data)
                except Exception as e:
                    parser_logger.error(f"Failed to change prices in {market.type}({market.name}). {e.__class__.__name__}: {e}")
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

@dataclass
class UpdateData:
    sku: int | None = None
    self_weight: int | None = None
    self_length: int | None = None
    self_width: int | None = None
    self_height: int | None = None
    description: str | None = None

async def foo(datas: dict[str, Any],
              scrab_data: pd.DataFrame,
              scrabBerries_data: pd.DataFrame) -> None:
    for data in datas:
        try:
            data_1, data_2 = None, None
            if len(scrab_row := scrab_data[scrab_data['sku'] == data['sku']]) == 1:
                data_1 = scrab_row.iloc[0].to_dict()
            if len(scrabBerries_row := scrabBerries_data[scrabBerries_data['sku'] == data['sku']]) == 1:
                data_2 = scrabBerries_row.iloc[0].to_dict()
            row = UpdateData(
                sku=data_1['sku'] if data_1 else data_2['sku'] if data_2 else None,
                self_weight=data_1['self_weight'] if data_1 and not np.isnan(data_1['self_weight']) else data_2['self_weight']
                        if data_2 and not np.isnan(data_2['self_weight']) else None,
                self_length=data_1['self_length'] if data_1 and not np.isnan(data_1['self_length']) else data_2['self_length']
                        if data_2 and not np.isnan(data_2['self_length']) else None,
                self_width=data_1['self_width'] if data_1 and not np.isnan(data_1['self_width']) else data_2['self_width']
                        if data_2 and not np.isnan(data_2['self_width']) else None,
                self_height=data_1['self_height'] if data_1 and (not isinstance(data_1['description'], str) and not np.isnan(data_1['self_height'])) else data_2['self_height']
                        if data_2 and not np.isnan(data_2['self_height']) else None,
                description=data_1['description'] if data_1 and not (not isinstance(data_1['description'], str) and np.isnan(data_1['description'])) else data_2['description']
                        if data_2 and not (not isinstance(data_1['description'], str) and np.isnan(data_2['description'])) else None,
            )
        except Exception as e:
            parser_logger.error(f"Failed to update data for {data['sku']}. {e.__class__.__name__}")
            raise e
        row.description = "'" + row.description + "'" if row.description is not None else None
        if row.sku:
            query = """
            UPDATE catalog_items
                SET self_weight=CASE
                    WHEN self_weight IS NULL THEN :self_weight
                    ELSE self_weight
                    END,
                self_length=CASE
                    WHEN self_length IS NULL THEN :self_length
                    ELSE self_length
                    END,
                self_width=CASE
                    WHEN self_width IS NULL THEN :self_width
                    ELSE self_width
                    END,
                self_height=CASE
                    WHEN self_height IS NULL THEN :self_height
                    ELSE self_height
                    END,
                description=CASE
                    WHEN description IS NULL THEN :description
                    ELSE description
                    END
            WHERE sku = :sku
            """
            async with get_db_session() as db_session:
                await db_session.execute(text(query), {
                    'self_weight': row.self_weight,
                    'self_length': row.self_length,
                    'self_width': row.self_width,
                    'self_height': row.self_height,
                    'description': row.description,
                    'sku': row.sku
                })
                await db_session.flush()


async def doo():
    catalog_repo = CatalogRepository()
    db_offers = []

    async with get_db_session() as db_session:
        catalog_repo.session = db_session
        async for chunk in catalog_repo.list():
            db_offers += [item.model_dump() for item in chunk]

    return db_offers

async def main():
    api_interactor = ApiInteractor(api_session_fabric=get_api_session,
                                   db_session_fabric=get_db_session)

    api_offers = await api_interactor.get_offers_list()
    api_offers_df = pd.DataFrame(api_offers)

    db_offers = await doo()

    scrab_offers = api_offers_df[api_offers_df['name_of_shop'] == 'Skrab']
    scrabBerries_offers = api_offers_df[api_offers_df['name_of_shop'] == 'SkrabBerries']

    await foo(db_offers, scrab_offers, scrabBerries_offers)
