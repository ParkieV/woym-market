from collections import defaultdict
from datetime import datetime
from math import ceil
from typing import Any

from aiohttp import ClientSession
from fastapi import HTTPException
from starlette import status

from logs import get_logger
from src.api.exceptions import InitializationError
from src.api.gateway_template import ApiGateway
from src.api.interfaces import IApiGateway, ApiTypes
from src.schemas.base_api_schemas import APIPriceChangeData, APIWarehouse, APIOffer, WarehouseType, APIWarehouseOffer, \
    APIOfferChangeData, APIOrderData

logger = get_logger(__name__, tags={'marketplace_api': 'wildberries'})


class WildberriesApi(ApiGateway, IApiGateway):
    market_type = 'Wildberries'
    __characteristic_ids = {
        'self_weight': 88953
    }

    def __init__(self, token: str, entity_id: int | None, shop_name: str, session: ClientSession) -> None: #type: ignore
        try:
            super().__init__(token, entity_id, shop_name, session)
            self.auth_headers = {
                'Authorization': self.token,
            }
        except InitializationError as err:
            raise InitializationError(ApiTypes.WILDBERRIES, err.detail)

    async def validate_auth_data(self):
        url = 'https://common-api.wildberries.ru/open-utils/tokens/introspect-v2'
        headers = {'X-Introspect': self.token}
        response = await self.request('GET', url=url, headers=headers)

        if not response.ok:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                f'Ошибка проверки данных авторизации сервиса {self.shop_name}(wildberries)')

        data = self.validate_response(response)
        if not data['Ok']:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                f'Ошибка проверки данных(токена) авторизации сервиса {self.shop_name}(wildberries)')

    async def change_offers(self, data: list[APIOfferChangeData]) -> None:

        items = await self._get_base_offer_data()
        items = {item['vendorCode']: item for item in items}

        update_url = 'https://content-api.wildberries.ru/content/v2/cards/update'

        def check_valid(x):
            return all((x.is_valid_name(), x.is_valid_description(), x.is_valid_vendor_code(), x.is_valid_sizes()))

        valid_offers_data, invalid_data = [], []
        for offer in data:
            if check_valid(offer):
                offer.name = offer.name[:60]
                offer.description = offer.description[:2000]
                valid_offers_data.append(offer)
            else:
                invalid_data.append(offer)

        if invalid_data:
            logger.warning(f'Invalid offers data: {len(invalid_data)} / {len(valid_offers_data)} {invalid_data}')

        if len(valid_offers_data) == 0:
            logger.warning(f'{self.shop_name}(wildberries) has no valid offers data')
            return

        chunk_size = 3000

        for i in range(0, len(valid_offers_data), chunk_size):
            body = []
            for offer_data in valid_offers_data[i:i + chunk_size]:
                characteristics = items[offer_data.sku].get('characteristics', [])
                characteristics = [i for i in characteristics if i['id'] != self.__characteristic_ids['self_weight']]
                characteristics.append({
                    "id": self.__characteristic_ids['self_weight'],
                    'value': offer_data.self_weight
                })

                body_item = {
                    'nmID': offer_data.vendor_code,
                    'vendorCode': offer_data.sku,
                    'brand': 'SKRAB',
                    'title': offer_data.name,
                    'description': offer_data.description,
                    'sizes': items[offer_data.sku]['sizes'],
                    'dimensions': {
                        'length': ceil(offer_data.self_length),
                        'width': ceil(offer_data.self_width),
                        'height': ceil(offer_data.self_height),
                    },
                    'characteristics': characteristics
                }
                body.append(body_item)

            response = await self.request('POST', url=update_url, body=body, headers=self.auth_headers, include_response_logs=True)

            if not response.ok:
                logger.error(f'Cant update offers data: {response.text}')
                continue

        errors = await self._errors_in_update()
        if errors:
            logger.error(f'Errors in offers: {errors}')

    async def get_offers_list(self) -> list[APIOffer]:
        offers = await self._get_offers_base_info()
        offers_prices = await self._get_offers_prices()

        result = []

        for offer in offers:
            offer.update(offers_prices[offer['sku']])
            result.append(
                APIOffer(**offer)
            )

        return result

    async def get_stocks(self) -> list[APIWarehouse]:
        warehouses = await self._get_warehouses()
        stocks = await self._get_stocks()

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
        result.append(APIWarehouse(market='wildberries', offers=[], name='Кластер все магазины', warehouse_type=WarehouseType.SUPER_CLUSTER))
        return result

    async def _check_price_update_result(self, task_id: int) -> None:
        if not task_id:
            logger.warning('Price task_id no gotten')
            return

        url = 'https://discounts-prices-api.wildberries.ru/api/v2/history/tasks'
        response = await self.request('GET', url=url, headers=self.auth_headers, params={'uploadID': task_id})

        if not response.ok:
            logger.error(f'Cant check price update result: {response.text}')

        response_json = await self.validate_response(response)

        if response_json.get('error', None):
            logger.error(f'Cant check price update result: {response_json.get("errorText", "unknown error")}')

        task_result_info = response_json.get('data', {})

        logger.info(
            f'Task price upload ID({task_result_info.get("uploadID", "unknown")}) with status: {task_result_info.get("status", "unknown")} checked. \nAll goods: {task_result_info.get("overAllGoodsNumber", "unknown")}, without errors: {task_result_info.get("successGoodsNumber", "unknown")}')

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
        valid_price_data = [price_data for price_data in data if price_data.is_valid_target_price() and price_data.is_valid_vendor_code()]
        invalid_price_data = [price_data for price_data in data if not (price_data.is_valid_target_price() and price_data.is_valid_vendor_code())]

        if invalid_price_data:
            logger.warning(f'Invalid price data: {len(invalid_price_data)} / {len(valid_price_data)} {invalid_price_data}')

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
            logger.info(body)
            response = await self.request('POST', url=url, body=body, headers=self.auth_headers, include_response_logs=True)

            if not response.ok:
                logger.error(f'Cant change price: {response.reason}: {await response.json()}')

            response_json = await self.validate_response(response)


            if response_json.get('data', None):
                await self._check_price_update_result(response_json['data'].get('id', None))

        logger.info(f'{self.shop_name}(wildberries) prices updated: {len(valid_price_data)} of {len(data)}')

    async def _get_base_offer_data(self) -> list[dict]:
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

            response = await self.request('POST', url=url, body=body, headers=self.auth_headers)

            if not response.ok:
                logger.error(f'Cant get offers base info: {response.text}')
                return result

            response_data = await self.validate_response(response)

            cards_data = response_data['cards']
            cursor_data = response_data['cursor']

            result.extend(cards_data)

            if cursor_data['total'] < limit:
                break

            if not all((cursor_data.get('updatedAt', None), cursor_data.get('nmID', None))):
                break

            cursor['updatedAt'] = cursor_data['updatedAt']
            cursor['nmID'] = cursor_data['nmID']

        return result

    async def _get_offers_base_info(self) -> list[dict]:
        items = await self._get_base_offer_data()
        result = []
        for item in items:
            self_weight = [i for i in item.get('characteristics', []) if
                             i.get('id', None) == self.__characteristic_ids['self_weight']]
            self_weight = self_weight[0].get('value', None) if self_weight else None

            offer = {
                'sku': item['vendorCode'],
                'name': item['title'],
                'description': item.get('description', None),
                'name_of_shop': self.shop_name,
                'market': 'wildberries',
                'self_length': ceil(item['dimensions']['length']),
                'self_width': ceil(item['dimensions']['width']),
                'self_height': ceil(item['dimensions']['height']),
                'self_weight': self_weight,
                'vendor_code': item['nmID'],
                'photo': item['photos'][0]['big'] if item.get('photos', None) else None,
                'barcodes': ', '.join([', '.join(size_info['skus']) for size_info in item['sizes']])

            }
            result.append(offer)

        return result

    async def _get_offers_prices(self) -> dict[str, Any]:
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter'

        limit = 1000
        offset = 0
        result = {}

        while True:
            response = await self.request('GET', url=url, params={'limit': limit, 'offset': offset}, headers=self.auth_headers)

            if not response.ok:
                logger.error(f'Cant get price info: {response.text}')
                break

            response_data = await self.validate_response(response)
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

    async def _get_warehouses(self) -> list[dict]:
        url = 'https://supplies-api.wildberries.ru/api/v1/warehouses'
        result = []

        response = await self.request('GET', url=url, headers=self.auth_headers)

        if not response.ok:
            logger.error(f'Cant get warehouses: {response.text}')
            return []

        response_data = await self.validate_response(response)

        for item in response_data:
            result.append({
                'market': 'wildberries',
                'name': item['name'],
                'warehouse_id': item['ID'],
                'warehouse_type': WarehouseType.WAREHOUSE,
            })

        return result

    async def _errors_in_update(self) -> list[dict]:
        url = 'https://content-api.wildberries.ru/content/v2/cards/error/list'
        response = await self.request('GET', url=url, headers=self.auth_headers)
        json_response = await self.validate_response(response)
        return json_response.get('data', [])

    async def _get_stocks_on_warehouse(self, warehouse_id: int, data: dict[str, Any]) -> list[APIWarehouseOffer]:
        url = f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouse_id}'
        result = []

        body = {
            'skus': list(data.keys())
        }
        response = await self.request('POST', url=url, headers=self.auth_headers, body=body)

        if not response.ok:
            logger.error(f'Cant get stocks on warehouse id({warehouse_id}): {response.text}')
            return result

        json_data = await self.validate_response(response)

        if not json_data['stocks']:
            return result

        for item in json_data['stocks']:
            result.append(APIWarehouseOffer(
                name_of_shop=self.shop_name,
                current_stock=item['amount'],
                sku=data[item['sku']]
            ))
        return result

    async def _get_stocks(self) -> defaultdict[Any, list]:
        date_from = '2000-06-20'
        url = f'https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom={date_from}'

        response = await self.request('GET', url=url, headers=self.auth_headers)
        if not response.ok:
            logger.error(f'Cant get stocks: {response.text}')
            return defaultdict()

        response_json = await self.validate_response(response)
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

    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        url = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom=2024-08-01'
        params = {
            'dateFrom': from_date.strftime('%Y-%m-%d'),
        }
        response = await self.request('GET', url=url, headers=self.auth_headers, params=params)

        if not response.ok:
            logger.error(f'Cant get orders from {from_date}: {response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалоь получить заказы: {response.text}')

        response_json = await self.validate_response(response)
        result = []

        for item in response_json:
            if item['orderType'] != 'Клиентский' and not item['isCancel']:
                continue

            order_item = APIOrderData(
                internal_order_id=str(item['gNumber']),
                sku=item['supplierArticle'],
                created_at=item['date'],
                updated_at=item.get('lastChangeDate', None),
                warehouse_name=item['warehouseName'],
                price=item.get('finishedPrice', None),
                quantity=1,
                market='wildberries',
                name_of_shop=self.shop_name

            )
            result.append(order_item)

        return result
