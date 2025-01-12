import pytest
from src.api.yandex.api import YandexMarketAPI
from tests.marketplaces.conftest import BaseMarketplaceAPITest


@pytest.mark.parametrize(
    'api_class,auth_data',
    [(YandexMarketAPI, {
        'token': 'y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU',
        'entity_id': 82457010,
        'shop_name': 'CALMARSHOP'
    })]
)
@pytest.mark.usefixtures('api')
class TestYandexMarketAPI(BaseMarketplaceAPITest):


    async def test_get_market_prices_report(self, api: YandexMarketAPI):
        id = api._get_business_id_by_campaign_id(api.entity_id)
        result = await api._get_market_prices_report(id)

        assert result

