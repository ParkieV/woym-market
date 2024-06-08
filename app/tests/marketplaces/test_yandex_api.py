import pytest
from src.api.yandex_market.api import YandexMarketAPI
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
    pass

