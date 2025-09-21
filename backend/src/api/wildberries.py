import asyncio
import inspect
from collections import defaultdict
from datetime import datetime
from math import ceil
from typing import Any, AsyncGenerator

from aiohttp import ClientSession
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from starlette import status
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random

from src.infra.policies.rate_limit import rate_limiter_gen
from src.infra.policies.timeout import DeadlineExceededError
from logs import parser_logger
from src.api.exceptions import InitializationError, RequestException, MarketplaceAPIException
from src.api.gateway_template import ApiGateway
from src.api.interfaces import IApiGateway, ApiTypes
from src.schemas.base_api_schemas import APIPriceChangeData, APIWarehouse, APIOffer, WarehouseType, APIWarehouseOffer, \
    APIOfferChangeData, APIOrderData



class WildberriesApi(ApiGateway, IApiGateway):
    market_type = 'Wildberries'

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

        data = self._get_resp_body_json()
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
            parser_logger.warning(f'Invalid offers data: {len(invalid_data)} / {len(valid_offers_data)}')

        if len(valid_offers_data) == 0:
            parser_logger.warning(f'{self.shop_name}(wildberries) has no valid offers data')
            return

        chunk_size = 3000

        for i in range(0, len(valid_offers_data), chunk_size):
            body = []
            for offer_data in valid_offers_data[i:i + chunk_size]:
                characteristics = items[offer_data.sku].get('characteristics', [])
                characteristics = [i for i in characteristics if i['id'] != 88952]

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
                        'weightBrutto': offer_data.self_weight,
                    },
                    'characteristics': characteristics
                }
                body.append(body_item)

            response = await self.request('POST', url=update_url, body=body, headers=self.auth_headers, include_response_logs=True)

            if not response.ok:
                parser_logger.error(f'Cant update offers data: {response.text}')
                continue

        errors = await self._errors_in_update()
        if errors:
            # ERROR: Источник - parser_2025-04-17.log:131
            parser_logger.error(f'Errors in offers: {errors}')

    async def get_offers_list(self) -> list[APIOffer]:
        offers = await self._get_offers_base_info()
        offers_prices = await self._get_offers_prices()
        offers_turnovers = {}
        try:
            async for turnover in self.get_turnover(
                [offer['vendor_code'] for offer in offers]
            ):
                offers_turnovers.update(turnover)
        except DeadlineExceededError:
            parser_logger.error(
                f"Method {inspect.currentframe().f_code.co_name} "
                "canceled by timeout policy"
            )
            offers_turnovers = {
                offer['vendor_code']: (None, None)
                for offer in offers
            }

        result = []
        # Не изменять, опасно!
        # Проверь, где используется
        turnover_default = {
            "hours": -3.0
        }

        for offer in offers:
            turnovers = offers_turnovers.get(
                offer['vendor_code'], (
                    turnover_default, turnover_default
                )
            )

            offer.update(offers_prices[offer['sku']])
            offer['turnover_avg_balance'] = turnovers[0]
            offer['turnover_curr_balance'] = turnovers[1]

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
                for i in stocks.get(
                    warehouse['name'] if warehouse['name'] != 'Краснодар (Тихорецкая)' else 'Краснодар',
                    [])
            ]
            result.append(
                APIWarehouse(
                    market='wildberries',
                    name=warehouse['name'],
                    offers=warehouse_stocks,
                    warehouse_type=WarehouseType.WAREHOUSE
                )
            )
        result.append(APIWarehouse(market='wildberries', offers=[], name='!Кластер все магазины', warehouse_type=WarehouseType.SUPER_CLUSTER))
        return result

    async def _check_price_update_result(self, task_id: int) -> None:
        if not task_id:
            parser_logger.warning('Price task_id no gotten')
            return

        url = 'https://discounts-prices-api.wildberries.ru/api/v2/history/tasks'
        response = await self.request('GET', url=url, headers=self.auth_headers, params={'uploadID': task_id})

        if not response.ok:
            parser_logger.error(f'Cant check price update result: {response.text}')

        response_json = await self._get_resp_body_json()

        if response_json.get('error', None):
            parser_logger.error(f'Cant check price update result: {response_json.get("errorText", "unknown error")}')

        task_result_info = response_json.get('data', {})

        parser_logger.info(
            f'Task price upload ID({task_result_info.get("uploadID", "unknown")}) with status: {task_result_info.get("status", "unknown")} checked. \nAll goods: {task_result_info.get("overAllGoodsNumber", "unknown")}, without errors: {task_result_info.get("successGoodsNumber", "unknown")}')

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
        valid_price_data = [price_data for price_data in data if price_data.is_valid_target_price() and price_data.is_valid_vendor_code()]
        invalid_price_data = [price_data for price_data in data if not (price_data.is_valid_target_price() and price_data.is_valid_vendor_code())]

        if invalid_price_data:
            parser_logger.warning(f'Invalid price data: {len(invalid_price_data)} / {len(valid_price_data)}')

        if not valid_price_data:
            parser_logger.warning(f'{self.shop_name}(wildberries) has no valid price data')
            return

        chunk_size = 1000

        for i in range(0, len(valid_price_data), chunk_size):
            body = {
                'data': []
            }
            for price_data in valid_price_data[i:i + chunk_size]:
                if price_data.sku == '20069':
                    pass
                data_dict = {
                    "nmID": price_data.vendor_code,
                }
                if price_data.target_price != price_data.api_current_price:
                    data_dict["price"] = round(price_data.target_price)
                if price_data.discount_changed is True:
                    data_dict["discount"] = int(price_data.discount)

                if len(data_dict.keys()) > 1:
                    body['data'].append(data_dict)
            if len(body['data']) > 0:
                response = await self.request('POST', url=url, body=body, headers=self.auth_headers, include_response_logs=True)

                if not response.ok:
                    parser_logger.error(f'Cant change price: {response.reason}: {await response.json()}')

                response_json = await self._get_resp_body_json(response)
                try:
                    if response_json.get('data') is not None and response_json['data'].get('id'):
                        await self._check_price_update_result(response_json['data'].get('id'))
                except Exception as e:
                    parser_logger.error(f'Cant change price: {e.__class__.__name__}: {e}')
                    raise e

        parser_logger.info(f'{self.shop_name}(wildberries) prices updated: {len(valid_price_data)} of {len(data)}')

    async def _get_base_offer_data(self) -> list[dict]:
        url = 'https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru'
        limit = 100
        cursor = {
            "limit": limit
        }

        result = []

        i = 0
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

            if i % 4 == 0:
                await asyncio.sleep(1)
            response = await self.request('POST', url=url, body=body, headers=self.auth_headers)
            await asyncio.sleep(1)

            if not response.ok:
                # ERROR: Здесь выкидывается ошибка 500
                #  пример: parser_2025-04-17.log:24
                parser_logger.error(f'Cant get offers base info: status {response.status}, {await response.text()}')
                return result

            response_data = await self._get_resp_body_json(response)

            cards_data = response_data['cards']
            cursor_data = response_data['cursor']

            result.extend(cards_data)

            if cursor_data['total'] < limit:
                break

            if not all((cursor_data.get('updatedAt', None), cursor_data.get('nmID', None))):
                break

            cursor['updatedAt'] = cursor_data['updatedAt']
            cursor['nmID'] = cursor_data['nmID']
            i += 1

        print('Result length:', len(result))
        return result

    async def _get_offers_base_info(self) -> list[dict]:
        items = await self._get_base_offer_data()
        result = []
        for item in items:
            self_weight = [i for i in item.get('characteristics', []) if
                             i.get('id', None) == 88953]
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
                parser_logger.error(f'Cant get price info: {response.text}')
                break

            response_data = await self._get_resp_body_json(response)
            data = response_data['data']['listGoods']

            if not data:
                parser_logger.error(f'Cant get price info: {response.text}')
                break

            for item in data:
                if not item['sizes']:
                    parser_logger.warning(f'Offer {item["vendorCode"]} has no sizes(price items)')
                    continue

                if len(item['sizes']) > 1:
                    parser_logger.warning(f'Offer {item["vendorCode"]} has more than one size(price item)')

                size = item['sizes'][0]

                result[item['vendorCode']] = {
                    'current_price': size['price'],
                    'your_promotion_price': size['discountedPrice'],
                    'seller_discount': item['discount'],
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
            parser_logger.error(f'Cant get warehouses: {response.text}')
            return []

        response_data = await self._get_resp_body_json(response)

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
        json_response = await self._get_resp_body_json(response)
        return json_response.get('data', [])

    async def _get_stocks_on_warehouse(self, warehouse_id: int, data: dict[str, Any]) -> list[APIWarehouseOffer]:
        url = f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouse_id}'
        result = []

        body = {
            'skus': list(data.keys())
        }
        response = await self.request('POST', url=url, headers=self.auth_headers, body=body)

        if not response.ok:
            parser_logger.error(f'Cant get stocks on warehouse id({warehouse_id}): {response.text}')
            return result

        json_data = await self._get_resp_body_json(response)

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
            parser_logger.error(f'Cant get stocks: {response.text}')
            return defaultdict()

        response_json = await self._get_resp_body_json(response)
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
            parser_logger.error(f'Cant get orders from {from_date}: {await response.text()}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалоь получить заказы: {await response.text()}')

        response_json = await self._get_resp_body_json(response)
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

    @retry(
        retry=retry_if_exception(ApiGateway._is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_random(0, 1),
        reraise=True
    )
    @rate_limiter_gen(max_rate=3, secs=61)
    async def get_turnover(
            self,
            vendor_codes: list[int],
            size: int | None = None,
            batch_size: int | None = 1000,
    ) -> AsyncGenerator[list[dict[str, float]], None]:
        """ Возвращает информацию об оборачиваемости остатков """
        if batch_size > 1000:
            raise ValueError("parameter \"batch_size\" must be less than or equal to 1000.")
        if size and size > len(vendor_codes):
            raise ValueError("parameter \"size\" must be less than or equal to length of skus.")
        if size and size < 0:
            raise ValueError("parameter \"size\" must be positive number.")

        if not vendor_codes:
            return

        offset = 0
        while True:
            # формирование запроса
            if size is not None:
                current_batch_size = min(batch_size, size - offset)
            else:
                current_batch_size = min(batch_size, len(vendor_codes) - offset)

            if current_batch_size < 1:
                return
            current_batch = vendor_codes[offset:offset + current_batch_size]
            offset += current_batch_size

            url = 'https://seller-analytics-api.wildberries.ru/api/v2/stocks-report/products/groups'
            body = {
                "nmIDs": current_batch,
                "currentPeriod": {
                    "start": (datetime.now() - relativedelta(months=1)).strftime('%Y-%m-%d'),
                    "end": datetime.now().strftime('%Y-%m-%d')
                },
                "stockType": "wb",
                "skipDeletedNm": True,
                "availabilityFilters": [
                    "deficient", "actual", "nonActual",
                    "balanced", "nonLiquid", "invalidData"
                ],
                "orderBy": {
                    "field": "ordersCount",
                    "mode": "desc"
                },
                "offset": 0
            }

            # отправка запроса
            response = await self.request('POST', url=url, headers=self.auth_headers, body=body)
            try:
                await self._validate_response(response)
            except RequestException as e:
                err_msg = f'Cant get turnover that starts with nmID={vendor_codes[0]}: {str(e)}'
                parser_logger.critical(err_msg)
                raise MarketplaceAPIException(api_type=str(ApiTypes.WILDBERRIES), details=err_msg)

            # обработка ответа
            result_batch = {}

            resp_body = await response.json()
            for group in resp_body["data"]["groups"]:
                for item in group['items']:
                    result_batch[item["nmID"]] = (
                        item["metrics"]["avgStockTurnover"] or {
                            "hours": -3.0
                        },
                        item["metrics"]["saleRate"] or {
                            "hours": -3.0
                        }
                    )
            yield result_batch
