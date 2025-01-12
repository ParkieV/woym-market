from abc import ABC

import pytest

from src.api.interfaces import IApiGateway
from src.schemas.base_api_schemas import APIOffer, APIWarehouse


@pytest.fixture(name='api')
def marketplace_api_instance(api_class: type[IApiGateway], auth_data: dict) -> IApiGateway:
    return api_class(**auth_data)  # type: ignore


class BaseMarketplaceAPITest(ABC):
    async def test_get_offers_list(self, api):
        offers = await api.get_offers_list()
        assert isinstance(offers, list)
        assert len(offers)
        assert isinstance(offers[0], APIOffer)

    async def test_get_stocks(self, api):
        stocks = await api.get_stocks()
        assert isinstance(stocks, list)
        assert len(stocks)
        assert isinstance(stocks[0], APIWarehouse)