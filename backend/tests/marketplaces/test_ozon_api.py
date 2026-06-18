import pytest
from unittest.mock import ANY, AsyncMock
from datetime import datetime, timedelta
from ...src.api.ozon import OzonApi
from src.schemas.base_api_schemas import APIOfferChangeData
from src.params.config import config
import pandas as pd  #noqa
    


@pytest.mark.parametrize(
    'api_class,auth_data',
    [(OzonApi, {
        'token': 'a66f89c1-73ef-487b-a051-f39875312fa2',
        'entity_id': 532844,
        'shop_name': 'Skarb'
    })]
)
@pytest.mark.usefixtures('api')
class TestOzonApi:

    async def test_get_offers_attributes(self, api: OzonApi):
        idents = []
        async for chunk in api._get_offers_attributes_by_chunks():
            idents += chunk
        attributes = api._get_offers_attributes(idents)
        assert isinstance(attributes, dict)

    # async def test_set_search_words(self, api: OzonApi):
    #     await api._set_search_words([('28165', 'секатор; сучкорез')])

    async def test_get_clasters_info(self, api: OzonApi):
        clasters = api._get_clusters_info()
        assert isinstance(clasters, list)
        assert len(clasters)

    async def test_get_orders(self, api: OzonApi):
        end = datetime.now(tz=config.time_zone_ino)
        start = end - timedelta(days=120)
        orders = await api.get_orders(start, end)

        assert isinstance(orders, list)
        assert orders

    async def test_change_offers(self, api: OzonApi):

        api._get_info_attributes = lambda x, y: {
            "123": {
                "id": 1,
                "name": "ItemA",
                "height": 1.,
                "depth": 4.,
                "width": 7,
                "dimension_unit": "cm",
                "weight": 1.,
                "weight_unit": "kg",
                "sku": 123,
                "images": [
                "123.jpg",
                "321.jpg"
                ],
                "attributes": [],
                "description_category_id": 123
            },
            "456": {
                "id": 2,
                "name": "ItemB",
                "height": 1.,
                "depth": 5.,
                "width": 8,
                "dimension_unit": "cm",
                "weight": 2.,
                "weight_unit": "kg",
                "sku": 456,
                "images": [
                "456.jpg",
                "654.jpg"
                ],
                "attributes": [],
                "description_category_id": 456
            },
            "789": {
                "id": 3,
                "name": "ItemC",
                "height": 1.,
                "depth": 6.,
                "width": 9,
                "dimension_unit": "cm",
                "weight": 3.,
                "weight_unit": "kg",
                "sku": 789,
                "images": [
                "789.jpg",
                "987.jpg"
                ],
                "attributes": [],
                "description_category_id": 789
            }
        }

        api._get_offers_prices_by_sku = lambda x, y: {
            "123": {
                "price": {
                "old_price": 123,
                "price": 321,
                "vat": 0.1
                },
            },
            "456": {
                "price": {
                "old_price": 456,
                "price": 654,
                "vat": 0.2
                },
            },
            "789": {
                "price": {
                "old_price": 789,
                "price": 987,
                "vat": 0.3
                },
            }
        }

        class APITestResponse:
            def __init__(self, body, OK: bool = True):
                self.ok = OK

                assert 'items' in body
                assert len(body['items']) == 3

                items = body['items']

                # ItemA (индекс 0)
                assert items[0]['name'] == 'ItemA'
                assert items[0]['height'] == 1
                assert items[0]['depth'] == 4
                assert items[0]['width'] == 7
                assert items[0]['dimension_unit'] == 'cm'
                assert items[0]['weight'] == 1
                assert items[0]['weight_unit'] == 'kg'
                assert items[0]['sku'] == 123
                assert items[0]['old_price'] == '123'
                assert items[0]['price'] == '321'
                assert items[0]['vat'] == '0.1'
                assert len(items[0]['images']) == 2
                assert items[0]['images'][0] == '123.jpg'
                assert items[0]['images'][1] == '321.jpg'
                assert len(items[0]['attributes']) == 2
                assert items[0]['attributes'][0]['id'] == 22336
                assert items[0]['attributes'][0]['complex_id'] == 0
                assert len(items[0]['attributes'][0]['values']) == 1
                assert items[0]['attributes'][0]['values'][0]['dictionary_value_id'] == 0
                assert items[0]['attributes'][0]['values'][0]['value'] == 'It is a search word'
                assert items[0]['attributes'][1]['id'] == 4191
                assert items[0]['attributes'][1]['values'][0]['value'] == ''
                assert items[0]['new_description_category_id'] == 123

                # ItemB (индекс 1)
                assert items[1]['name'] == 'ItemB'
                assert items[1]['height'] == 1
                assert items[1]['depth'] == 5
                assert items[1]['width'] == 8
                assert items[1]['dimension_unit'] == 'cm'
                assert items[1]['weight'] == 2
                assert items[1]['weight_unit'] == 'kg'
                assert items[1]['sku'] == 456
                assert items[1]['old_price'] == '456'
                assert items[1]['price'] == '654'
                assert items[1]['vat'] == '0.2'
                assert len(items[1]['images']) == 2
                assert items[1]['images'][0] == '456.jpg'
                assert items[1]['images'][1] == '654.jpg'
                assert len(items[1]['attributes']) == 2
                assert items[1]['attributes'][0]['id'] == 23171
                assert items[1]['attributes'][0]['complex_id'] == 0
                assert items[1]['attributes'][0]['values'][0]['value'] == '#It_may_be_hashtag'
                assert items[1]['attributes'][1]['id'] == 4191
                assert items[1]['attributes'][1]['values'][0]['value'] == ''
                assert items[1]['new_description_category_id'] == 456

                # ItemC (индекс 2)
                assert items[2]['name'] == 'ItemC'
                assert items[2]['height'] == 1
                assert items[2]['depth'] == 6
                assert items[2]['width'] == 9
                assert items[2]['dimension_unit'] == 'cm'
                assert items[2]['weight'] == 3
                assert items[2]['weight_unit'] == 'kg'
                assert items[2]['sku'] == 789
                assert items[2]['old_price'] == '789'
                assert items[2]['price'] == '987'
                assert items[2]['vat'] == '0.3'
                assert len(items[2]['images']) == 2
                assert items[2]['images'][0] == '789.jpg'
                assert items[2]['images'][1] == '987.jpg'
                assert len(items[2]['attributes']) == 2
                assert items[2]['attributes'][0]['id'] == 23171
                assert items[2]['attributes'][0]['complex_id'] == 0
                assert items[2]['attributes'][0]['values'][0]['value'] == '#It_is_hashtag'
                assert items[2]['attributes'][1]['id'] == 4191
                assert items[2]['attributes'][1]['values'][0]['value'] == ''
                assert items[2]['new_description_category_id'] == 789

        api.request = lambda self, reqtype, url, body, headers, include_response_logs: APITestResponse(body)
        api._get_resp_body_json = lambda self, x: {"result": {"task_id": "12345"}}
        api.check_task_status = lambda self, id: True

        # --- Входные данные ---
        data = [APIOfferChangeData() for i in range(3)]
        parameters = [
                'sku', 'market', 'name_of_shop', 'name', 
                'description', 'vendor_code', 'search_words', 'hashtags', 
                'barcodes', 'self_weight', 'self_length', 'self_width', 'self_height']

        values = [
            ('123', '456', '789'),
            ('ozon', 'ozon', 'ozon'),
            ('Ozonya', 'Ozonya', 'Ozonya'),
            ('ItemA', 'ItemB', 'ItemC'),
            ('', '', ''),
            (222, 333, 444),
            ('It is a search word', 'It is not search word', ''),
            ('', '#It_may_be_hashtag', '#It_is_hashtag'),
            ('', '', ''),
            (1., 2., 3.),
            (4., 5., 6.),
            (7., 8., 9.),
            (1., 1., 1.)
        ]

        for param, tval in zip(parameters, values):
            for i in range(len(data)):
                setattr(data[i], param, tval[i])

        # --- Тест ---
        await api.change_offers(data)
        

    async def test_get_offers_list(self, api: OzonApi):
        offers = await api.get_offers_list()
        assert isinstance(offers, list)
        assert offers
