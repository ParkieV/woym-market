from collections import defaultdict
from typing import Any

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
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                f'Ошибка проверки данных авторизации сервиса {self.shop_name}(wildberries)')

        data = response.json()
        if not data['Ok']:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                f'Ошибка проверки данных(токена) авторизации сервиса {self.shop_name}(wildberries)')

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

    def _check_price_update_result(self, task_id: int) -> None:
        if not task_id:
            logger.warning('Price task_id no gotten')
            return

        url = 'https://discounts-prices-api.wildberries.ru/api/v2/history/tasks'
        response = self.session.get(url, headers=self.auth_headers, params={'uploadID': task_id})

        if not response.ok:
            logger.error(f'Cant check price update result: {response.text}')

        response_json = response.json()

        if response_json.get('error', None):
            logger.error(f'Cant check price update result: {response_json.get("errorText", "unknown error")}')

        task_result_info = response_json.get('data', {})

        logger.info(
            f'Task price upload ID({task_result_info.get("uploadID", "unknown")}) with status: {task_result_info.get("status", "unknown")} checked. \nAll goods: {task_result_info.get("overAllGoodsNumber", "unknown")}, without errors: {task_result_info.get("successGoodsNumber", "unknown")}')

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
        valid_price_data = [price_data for price_data in data if
                            price_data.is_valid_target_price() and price_data.is_valid_vendor_code()]

        if not valid_price_data:
            logger.warning(f'{self.shop_name}(wildberries) has no valid price data')
            return

        chunk_size = 1000

        for i in range(0, len(valid_price_data), chunk_size):
            body = {
                'data': [
                    {
                        "nmID": price_data.vendor_code,
                        "price": round(price_data.target_price),
                    }
                    for price_data in valid_price_data[i:i + chunk_size]
                ]
            }
            response = self.session.post(url, json=body, headers=self.auth_headers)

            if not response.ok:
                logger.error(logger.error(f'Cant change price: {response.text}'))

            response_json = response.json()

            if response_json.get('error', None):
                logger.error(response_json['errorText'])

            if response_json.get('data', None):
                self._check_price_update_result(response_json['data'].get('id', None))

        logger.info(f'{self.shop_name}(wildberries) prices updated: {len(valid_price_data)} of {len(data)}')

    def _get_offers_base_info(self) -> list[dict]:
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
                logger.error(f'Cant get offers base info: {response.text}')
                return result

            response_data = response.json()

            cards_data = response_data['cards']
            cursor_data = response_data['cursor']

            for item in cards_data:
                yandex_weight = [i for i in item.get('characteristics', []) if
                                 i.get('id', None) == self.__characteristic_ids['yandex_weight']]
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

    def _get_offers_prices(self) -> dict[str, Any]:
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter'

        limit = 1000
        offset = 0
        result = {}

        while True:
            response = self.session.get(url, params={'limit': limit, 'offset': offset}, headers=self.auth_headers)

            if not response.ok:
                logger.error(f'Cant get price info: {response.text}')
                break

            response_data = response.json()
            data = response_data['data']['listGoods']

            if not data:
                logger.error(f'Cant get price info: {response.text}')
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
            logger.error(f'Cant get warehouses: {response.text}')
            return []

        response_data = response.json()

        for item in response_data:
            result.append({
                'market': 'wildberries',
                'name': item['name'],
                'warehouse_id': item['ID'],
                'warehouse_type': WarehouseType.WAREHOUSE,
            })

        return result

    def _get_stocks_on_warehouse(self, warehouse_id: int, data: dict['barcode', 'sku']) -> list[APIWarehouseOffer]:
        url = f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouse_id}'
        result = []

        body = {
            'skus': list(data.keys())
        }
        response = self.session.post(url, headers=self.auth_headers, json=body)

        if not response.ok:
            logger.error(f'Cant get stocks on warehouse id({warehouse_id}): {response.text}')
            return result

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

    def _get_stocks(self) -> defaultdict[str, dict[str, Any]]:
        date_from = '2000-06-20'
        url = f'https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom={date_from}'

        response = self.session.get(url, headers=self.auth_headers)
        if not response.ok:
            logger.error(f'Cant get stocks: {response.text}')
            return []

        response_json = response.json()
        result = defaultdict(list)

        if not response_json:
            return result

        for item in response_json:
            result[item['warehouseName']].append(
                {
                    'sku': item['supplierArticle'],
                    'current_stock': item['quantity'],  # может быть 'quantityFull'
                }
            )

        return result
