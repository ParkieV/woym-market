import pytest

from src.api.wildberries.api import WildberriesAPI
from src.schemas.base_api_schemas import APIWarehouse
from tests.marketplaces.conftest import BaseMarketplaceAPITest


@pytest.mark.parametrize(
    'api_class,auth_data',
    [(WildberriesAPI, {
        'token': 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwODAxdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTczODc5ODI5NiwiaWQiOiI3OTJlNDEwYi05NWU3LTRiMzgtOGNjMC01NzU2YzU1YTAxODIiLCJpaWQiOjMzMzQ2Mzk1LCJvaWQiOjIxODM3OCwicyI6ODE5MCwic2lkIjoiMTQ1ZTUwYWQtM2YyZS00MzE1LTkxMDQtZDhlMTAyN2E3MGFmIiwidCI6ZmFsc2UsInVpZCI6MzMzNDYzOTV9.WD9bOKfDSUD6mll5zUAG-1i_fj-QYZUQl4zX8OGuhigZtZN3RdAYL_kglYJ2iJsMZ0-qzUztY9dqTiKcTRz3KQ',
        'shop_name': 'Skarb'
    })]
)
@pytest.mark.usefixtures('api')
class TestWildberriesAPI(BaseMarketplaceAPITest):
    def test_get_offers_base_info(self, api: WildberriesAPI):
        offers = api._get_offers_base_info()
        assert isinstance(offers, list)
        assert len(offers)
        assert isinstance(offers[0], dict)

    def test_get_warehouse(self, api: WildberriesAPI):
        warehouses = api._get_warehouse()
        assert isinstance(warehouses, list)
        assert len(warehouses)
        assert isinstance(warehouses[0], APIWarehouse)

    def test_get_offers_prices(self, api: WildberriesAPI):
        prices = api._get_offers_prices()
        assert isinstance(prices, dict)
        assert len(prices)




