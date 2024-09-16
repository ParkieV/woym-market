import pytest
from datetime import datetime, timedelta
from src.api.ozon.api import OzonAPI
from src.schemas.base_api_schemas import APIOfferChangeData
from tests.marketplaces.conftest import BaseMarketplaceAPITest
from src.params.confing import config
import pandas as pd  #noqa


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

    async def test_get_clasters_info(self, api: OzonAPI):
        clasters = api._get_clasters_info()
        assert isinstance(clasters, list)
        assert len(clasters)

    async def test_get_orders(self, api: OzonAPI):
        end = datetime.now(tz=config.time_zone_ino)
        start = end - timedelta(days=120)
        orders = await api.get_orders(start, end)

        assert isinstance(orders, list)
        assert orders

    async def test_change_offers(self, api: OzonAPI):
        data = [
            APIOfferChangeData(
                sku='26714',
                market='ozon',
                name_of_shop='Skrab',
                name='Нож строительный',
                description='Описание',
                search_words='нож строительный',
                self_weight='0.09',
                self_length='20',
                self_width='10',
                self_height='4',
            )
        ]
        await api.change_offers(data)
