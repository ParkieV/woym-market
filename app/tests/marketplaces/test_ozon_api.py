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

    async def test_get_offers_attributes(self, api: OzonAPI):
        idents = api._get_offers_identifiers()
        attributes = api._get_offers_attributes(idents)
        assert isinstance(attributes, dict)


    # async def test_set_search_words(self, api: OzonAPI):
    #     await api._set_search_words([('28165', 'секатор; сучкорез')])
