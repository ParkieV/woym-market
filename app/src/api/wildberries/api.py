from collections import defaultdict

from fastapi import HTTPException
from requests import Session
from starlette import status

from logs import get_logger
from src.api.base_api import BaseAPI
from src.schemas.base_api_schemas import APIPriceChangeData, APIWarehouse, APIOffer, WarehouseType, APIWarehouseOffer

logger = get_logger(__name__)


class WildberriesAPI(BaseAPI):
    __characteristic_ids = {
        'yandex_weight': 88953
    }

    def __init__(self, token: str, shop_name: str, *args, **kwargs):
        self.token = token
        self.shop_name = shop_name
        self.auth_headers = {
            'Authorization': self.token,
        }
        self.session = Session()

    async def validate_auth_data(self, **kwargs):
        url = 'https://common-api.wildberries.ru/open-utils/tokens/introspect-v2'
        headers = {'X-Introspect': self.token}
        response = self.session.get(url, headers=headers)

        if not response.ok:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f'Ошибка проверки данных авторизации сервиса {self.shop_name}(wildberries)')

        data = response.json()
        if not data['Ok']:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f'Ошибка проверки данных(токена) авторизации сервиса {self.shop_name}(wildberries)')

    async def get_offers_list(self) -> list[APIOffer]:
        offers = self._get_offers_base_info()
        offers_prices = self._get_offers_prices()

        result = []

        for offer in offers:
            offer.update(offers_prices[offer['sku']])
            result.append(
                APIOffer(**offer)
            )

        return result

    async def get_stocks(self) -> list[APIWarehouse]:
        warehouses = self._get_warehouses()
        stocks = self._get_stocks()

        result = []

        for warehouse in warehouses:
            warehouse_stocks = [
                APIWarehouseOffer(name_of_shop=self.shop_name, **i)
                for i in stocks.get(warehouse['name'], [])
            ]
            result.append(
                APIWarehouse(
                    market='wildberries',
                    name=warehouse['name'],
                    offers=warehouse_stocks,
                    warehouse_type=WarehouseType.WAREHOUSE
                )
            )
        return result


    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
        valid_price_data = [price_data for price_data in data if price_data.is_valid_target_price()]

        chunk_size = 1000

        for i in range(0, len(valid_price_data), chunk_size):
            body = {
                'data': [
                    {
                        "nmID": price_data.vendor_code,
                        "price": price_data.target_price,
                        "discount": 0
                    }
                    for price_data in valid_price_data[i:i + chunk_size]
                ]
            }
            # response = self.session.post(url, json=body, headers=self.auth_headers)
            #
            # if not response.ok:
            #     #TODO
            #     raise

    def _get_offers_base_info(self):
        url = 'https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru'

        limit = 100
        cursor = {
            "limit": limit,
            "nmID": 0,
        }

        result = []

        while True:
            body = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "cursor": cursor,
                    "filter": {
                        "withPhoto": -1
                    }
                }
            }

            response = self.session.post(url, json=body, headers=self.auth_headers)

            if not response.ok:
                # TODO
                break

            response_data = response.json()

            cards_data = response_data['cards']
            cursor_data = response_data['cursor']

            for item in cards_data:
                yandex_weight = [i for i in item.get('characteristics', []) if i.get('id', None) == self.__characteristic_ids['yandex_weight']]
                yandex_weight = yandex_weight[0].get('value', None) if yandex_weight else None

                offer = {
                    'sku': item['vendorCode'],
                    'name': item['title'],
                    'name_of_shop': self.shop_name,
                    'market': 'wildberries',
                    'yandex_length': item['dimensions']['length'],
                    'yandex_width': item['dimensions']['width'],
                    'yandex_height': item['dimensions']['height'],
                    'yandex_weight': yandex_weight,
                    'vendor_code': item['nmID'],
                    'photo': item['photos'][0]['big'] if item.get('photos', None) else None,
                    'barcodes': ', '.join([', '.join(size_info['skus']) for size_info in item['sizes']])

                }
                result.append(offer)

            if cursor_data['total'] < limit:
                break

            if not all((cursor_data.get('updatedAt', None), cursor_data.get('nmID', None))):
                break

            cursor['updatedAt'] = cursor_data['updatedAt']
            cursor['nmID'] = cursor_data['nmID']

        return result

    def _get_offers_prices(self):
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter'

        limit = 1000
        offset = 0
        result = {}

        while True:
            response = self.session.get(url, params={'limit': limit, 'offset': offset}, headers=self.auth_headers)

            if not response.ok:
                # TODO
                break

            response_data = response.json()
            data = response_data['data']['listGoods']

            if not data:
                break

            for item in data:
                if not item['sizes']:
                    logger.warning(f'Offer {item["vendorCode"]} has no sizes(price items)')
                    continue

                if len(item['sizes']) > 1:
                    logger.warning(f'Offer {item["vendorCode"]} has more than one size(price item)')

                size = item['sizes'][0]

                result[item['vendorCode']] = {
                    'current_price': size['price'],
                    'your_promotion_price': size['discountedPrice'],
                }

            if len(data) < limit:
                break

            offset += limit

        return result

    def _get_warehouses(self) -> list[dict]:
        url = 'https://supplies-api.wildberries.ru/api/v1/warehouses'
        result = []

        response = self.session.get(url, headers=self.auth_headers)

        if not response.ok:
            # TODO
            return

        response_data = response.json()

        for item in response_data:
            result.append({
                'market': 'wildberries',
                'name': item['name'],
                'warehouse_id': item['ID'],
                'warehouse_type': WarehouseType.WAREHOUSE,
            })

        return result

    def _get_stocks_on_warehouse(self, warehouse_id: int,  data: dict['barcode', 'sku']) -> list[APIWarehouseOffer]:
        url = f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouse_id}'
        body = {
            'skus': list(data.keys())
        }
        response = self.session.post(url, headers=self.auth_headers, json=body)

        if not response.ok:
            # TODO
            raise
        result = []

        json_data = response.json()

        if not json_data['stocks']:
            return result

        for item in json_data['stocks']:
            result.append(APIWarehouseOffer(
                name_of_shop=self.shop_name,
                current_stock=item['amount'],
                sku=data[item['sku']]
            ))
        return result


    def _get_stocks(self):
        date_from = '2000-06-20'
        url = f'https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom={date_from}'

        response = self.session.get(url, headers=self.auth_headers)
        if not response.ok:
            raise

        response_json = response.json()
        result = defaultdict(list)

        if not response_json:
            return result

        for item in response_json:
            result[item['warehouseName']].append(
                {
                    'sku': item['supplierArticle'],
                    'current_stock': item['quantity'], # может быть 'quantityFull'
                }
            )

        return result

