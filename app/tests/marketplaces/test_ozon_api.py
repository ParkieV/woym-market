import pytest

from src.api.ozon.api import OzonAPI
from tests.marketplaces.conftest import BaseMarketplaceAPITest


@pytest.mark.parametrize(
    'api_class,auth_data',
    [(OzonAPI, {
        'token': 'a66f89c1-73ef-487b-a051-f39875312fa2',
        'entity_id': 532844,
        'shop_name': 'Skarb'
    })]
)
@pytest.mark.usefixtures('api')
class TestOzonAPI(BaseMarketplaceAPITest):
    pass
