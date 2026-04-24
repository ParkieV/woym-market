import asyncio
from enum import Enum
from math import ceil
from typing import Any, AsyncIterator
from datetime import datetime
from dataclasses import dataclass
from collections.abc import Sequence, Mapping, AsyncGenerator

from aiohttp import ClientSession
from starlette import status
from fastapi import HTTPException
from tenacity import retry_if_exception, retry, stop_after_attempt, wait_random

from src.infra.formatters import html_to_md_linear
from src.api.exceptions import MarketplaceAPIException, RequestException
from src.infra.policies.rate_limit import rate_limiter_gen
from logs import parser_logger
from src.api.exceptions import InitializationError
from src.api.interfaces import IApiGateway, ApiTypes
from src.api.gateway_template import ApiGateway, get_api_session
from src.schemas.base_api_schemas import APIOffer, APIWarehouseOffer, APIWarehouse, APIPriceChangeData, WarehouseType, \
    APIOfferChangeData, APIOrderData



@dataclass
class OfferIdentifier:
    product_id: int
    offer_id: str

class AttributeIdentifications(Enum):
    hashtag = 23171
    description = 4191
    search_words = 22336


class OzonApi(ApiGateway, IApiGateway):
    market_type = 'Ozon'

    def __init__(self, token: str, entity_id: str | None, shop_name: str, session: ClientSession) -> None: #type: ignore
        try:
            super().__init__(token, entity_id, shop_name, session)
        except InitializationError as err:
            raise InitializationError(ApiTypes.OZON, err.detail)

    async def _get_info_attributes(self, skus: Sequence[str] | None = None) -> dict[str, Any]:
        """
        Получаем информацию о карточках с соответствующим СКУ.
        :param skus: Список СКУ товаров.
        :return: Информация о товарах;
        """
        url = 'https://api-seller.ozon.ru/v4/product/info/attributes'
        chunk_size = 1000
        for l in range(0, len(skus), chunk_size):
            body = {
                'filter': {
                    'offer_id': skus[l:min(l + chunk_size, len(skus))] if len(skus) > 0 else []
                },
                'limit': chunk_size
            }

            results = {}

            while True:
                response = await self.request('POST', url=url, body=body, headers=self.auth_headers)
                await asyncio.sleep(1)

                if not response.ok:
                    parser_logger.error(f'Error body: {body}')
                    parser_logger.error(f'Cant get info attributes: {response.text}')
                    break

                json_response = await response.json()

                for item in json_response.get('result', []):
                    results[item['offer_id']] = item

                last_id = json_response.get('last_id', None)
                if not last_id:
                    break

                body['last_id'] = last_id

            return results

    async def _get_offers_prices_by_sku(self, data: Sequence[str] | None = None) -> dict[str, Any]:
        """
        Получить информацию о цене товаров со соответствующим СКУ и её составляющих.
        :param data: Список СКУ товаров.
        :return: Информация о цене товаров
        """
        url = 'https://api-seller.ozon.ru/v5/product/info/prices'
        results = {}
        chunk_size = 1000
        for l in range(0, len(data), chunk_size):
            body = {
                "filter": {
                    "offer_id": data[l:min(l + chunk_size, len(data))] if len(data) > 0 else [],
                    "visibility": "ALL"
                },
                "limit": chunk_size
            }
            while True:
                response = await self.request('POST', url=url, body=body, headers=self.auth_headers)
                if not response.ok:
                    parser_logger.error(f'Cant collect offers price info: {response.text}')
                    break

                json_response = await response.json()

                for item in json_response.get('items', []):
                    results[item['offer_id']] = item

                last_id = json_response.get('cursor', None)
                if not last_id or json_response.get('total', 0) < chunk_size:
                    break

                body['cursor'] = last_id

        return results

    async def _get_offers_prices_by_identifiers(self, offer_data: Sequence[OfferIdentifier]) -> dict[str, dict]:
        chunk_size = 1000
        result = dict()

        for i in range(0, len(offer_data), chunk_size):
            body = {
                'filter': {
                    'offer_id': [i.offer_id for i in offer_data[i:i + chunk_size]]
                },
                'limit': chunk_size
            }
            response = await self.request('POST', url='https://api-seller.ozon.ru/v5/product/info/prices', headers=self.auth_headers,
                                         body=body)

            data = await self._get_resp_body_json(response, body=body)

            for offer in data['items']:
                result[offer['offer_id']] = {
                    'marketing_seller_price': self._str_to_float(offer['price'].get('marketing_seller_price', None))
                }

                try:
                    commissions = offer['commissions']

                    sales_percent = commissions['sales_percent_fbo']
                    price = self._str_to_float(offer['price']['price'])

                    expenses = commissions['fbo_direct_flow_trans_min_amount']

                    result[offer['offer_id']]['commissions'] = price * sales_percent / 100 + expenses

                except Exception:
                    parser_logger.error(f'Error in get commission for offer with sku {offer["offer_id"]}', exc_info=True)

        return result

    async def _get_content_ratings(self, skus: Sequence[int]):
        chunk_size = 100
        result = {}

        for i in range(0, len(skus), chunk_size):
            body = {
                'skus': skus[i:i + chunk_size]
            }
            response = await self.request('POST', url='https://api-seller.ozon.ru/v1/product/rating-by-sku',
                                         headers=self.auth_headers, body=body)
            await asyncio.sleep(1)
            data = await self._get_resp_body_json(response, body=body)
            result.update({item['sku']: item['rating'] for item in data['products']})

        return result

    async def _get_stock_on_warehouses(self):
        chunk_size = 1000
        offset = 0
        result = []

        while True:
            body = {
                'limit': chunk_size,
                'offset': offset,
                'warehouse_type': 'ALL'
            }
            response = await self.request('POST', url='https://api-seller.ozon.ru/v2/analytics/stock_on_warehouses',
                                         headers=self.auth_headers, body=body)

            data = await self._get_resp_body_json(response, body)
            await asyncio.sleep(1)
            if not data['result']['rows']:
                break

            for stock in data['result']['rows']:
                stock_data = {
                    'value': stock['free_to_sell_amount'],
                    'market_sku': stock['sku'],
                    'warehouse_name': self._validate_warehouse_name(stock['warehouse_name'])
                }
                result.append(stock_data)

            offset += chunk_size

        return result

    async def _market_sku_to_offer_id(self) -> Mapping[int, str]:
        offers_identifiers = []
        async for chunk in self._get_offers_identifiers_by_chunks():
            offers_identifiers += chunk
        offers = await self._get_offers_base_info(offers_identifiers)

        return {offer['market_sku']: offer['sku'] for offer in offers if offer['market_sku'] != 0}

    def _validate_warehouse_name(self, warehouse_name: str) -> str:
        abbreviations = ('рфц', 'мпсц', 'мрфц')
        result_name = ' '.join(
            name.title() if name.lower() not in abbreviations else name.upper()
            for name in warehouse_name.split('_')
        )
        return result_name

    async def _get_clusters_info(self) -> list[APIWarehouse]:
        # url = 'https://seller-edu.ozon.ru/document-manager-api.kms/api/v2/seller-edu/document/public/by-path?path=%2Ffbo%2Fwarehouses%2Ftable-klastery'
        url = 'https://api-seller.ozon.ru/v1/cluster/list'
        response = await self.request(
            'POST', url=url, headers=self.auth_headers,
            body={
                    "cluster_type": "CLUSTER_TYPE_OZON"
            }
        )

        data = await self._get_resp_body_json(response)
        clusters = []
        for cluster in data['clusters']:
            clusters.append(
                APIWarehouse(name=cluster['name'], market='ozon', offers=[], warehouse_type=WarehouseType.CLUSTER,
                             related_warehouses_name=[
                                 self._validate_warehouse_name(warehouse['name'])
                                 for lc in cluster['logistic_clusters']
                                 for warehouse in lc['warehouses'] if warehouse['type'] == 'FULL_FILLMENT'
                             ]))

        return clusters

    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        """
        Изменение информации о карточках в магазине
        :param data: Данные для обновления
        """
        url = 'https://api-seller.ozon.ru/v3/product/import'

        # Лямбда-выражение, определяющее корректность данных карточек
        def is_valid_offer_data(x):
            return all((x.is_valid_name(), x.is_valid_description(), x.is_valid_search_words(), x.is_valid_sizes()))

        valid_data = [i for i in data if is_valid_offer_data(i)]
        invalid_data = [i for i in data if not is_valid_offer_data(i)]

        if invalid_data:
            parser_logger.error(f'Invalid offers data: {len(invalid_data)} / {len(valid_data)}')

        if len(valid_data) == 0:
            parser_logger.warning(f'{self.shop_name}(ozon) has no valid offers data')
            return

        # Получение информации об офферах с магазина
        offers_attributes_info = await self._get_info_attributes([i.sku for i in valid_data])
        offers_prices_info = await self._get_offers_prices_by_sku([i.sku for i in valid_data])

        to_update_offers_data = []

        # Подготовка моделей для отправки в магазины
        for valid_offer in valid_data:
            offer_price_info = offers_prices_info.get(valid_offer.sku, None)
            offer_attributes_info = offers_attributes_info.get(valid_offer.sku, None)

            if not offer_attributes_info or not offer_price_info:
                log_msg = 'Skip update offer sku={0} due to has no full data'.format(
                    offer_attributes_info.get("offer_id", "unknown") if offer_attributes_info
                    else offer_price_info.get("offer_id", "unknown")
                )
                parser_logger.info(log_msg)
                continue

            update_offer_data = offer_attributes_info
            update_offer_data.pop('id')
            update_offer_data['price'] = str(offer_price_info['price']['price'])
            update_offer_data['old_price'] = str(offer_price_info['price']['old_price'])
            update_offer_data['vat'] = str(offer_price_info['price']['vat'])
            update_offer_data['name'] = valid_offer.name
            update_offer_data['images'] = update_offer_data.get('images', [])
            update_offer_data['new_description_category_id'] = update_offer_data['description_category_id']

            update_offer_data['height'] = ceil(valid_offer.self_height)
            update_offer_data['width'] = ceil(valid_offer.self_width)
            update_offer_data['depth'] = ceil(valid_offer.self_length)
            update_offer_data['dimension_unit'] = 'cm'

            weight = valid_offer.self_weight
            weight_unit = 'kg'

            if weight % 1 > 0:
                weight *= 1000
                weight_unit = 'g'

            if weight % 1 > 0:
                parser_logger.error(f'Error in offer dimension weight={weight} weight_unit={weight_unit}. Cant parse to Integer.')
                continue

            update_offer_data['weight'] = int(weight)
            update_offer_data['weight_unit'] = weight_unit

            update_offer_data['attributes'] = update_offer_data.get('attributes', [])

            for attr in update_offer_data['attributes']:
                attr['id'] = attr.pop('id')

            for complex_attrs in update_offer_data['complex_attributes']:
                    complex_attrs['id'] = complex_attrs.pop('id')

            update_offer_data['attributes'] = [attr for attr in update_offer_data['attributes'] if attr['id'] not in (
                AttributeIdentifications.hashtag, AttributeIdentifications.description
            )]
            update_offer_data['attributes'].extend(
                [
                    {
                        "id": AttributeIdentifications.hashtag,
                        "complex_id": 0,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": valid_offer.search_words
                            }
                        ]
                    },
                    {
                        "id": AttributeIdentifications.description,
                        "complex_id": 0,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": valid_offer.description
                            }
                        ]
                    }
                ]
            )

            to_update_offers_data.append(update_offer_data)

        chunk_size = 100

        # Отправка данных в магазин
        for i in range(0, len(to_update_offers_data), chunk_size):
            body = {
                'items': [offer_data for offer_data in to_update_offers_data[i:i + chunk_size]]
            }
            response = await self.request('POST', url, body=body, headers=self.auth_headers, include_response_logs=True)
            if not response.ok:
                parser_logger.error(f'Cant update offers data: {response.text}')
                continue

            json_response = await self._get_resp_body_json(response)
            task_id = json_response.get('result', {}).get('task_id', None)
            if not task_id:
                parser_logger.error(f'Cant find task_id: {response.text}')
                return

            await asyncio.sleep(5)
            await self.check_task_status(task_id)

    async def check_task_status(self, task_id: int) -> None:
        if not task_id:

            return

        body = {
            'task_id': task_id,
        }
        response = await self.request('POST', url='https://api-seller.ozon.ru/v1/product/import/info', body=body, headers=self.auth_headers, include_response_logs=True)

        if not response.ok:
            parser_logger.error(f'Cant check task({task_id}) status {response.text}')
            return

        json_response = await self._get_resp_body_json(response)

        for item_info in json_response.get('result', {}).get('items', []):
            if item_info.get('status') == 'failed':
                parser_logger.error(
                    f'Offer {item_info.get("offer_id", "unknown")} was loaded with errors: {item_info.get("errors", "unknown")}')

            elif item_info.get('status') == 'pending':
                parser_logger.warning(f'Offer {item_info.get("offer_id", "unknown")} is still in pending')

        parser_logger.info(f'Task {task_id} checked. Total {json_response.get("result", {}).get("total", "unknown")}')

    async def get_offers_list(self) -> list[APIOffer]:
        offers_identifiers: list[OfferIdentifier] = []
        async for chunk in self._get_offers_identifiers_by_chunks():
            offers_identifiers += chunk
        offers = await self._get_offers_base_info(offers_identifiers)
        offers_attributes = await self._get_offers_attributes(offers_identifiers)
        offers_content_rating = await self._get_content_ratings(
            [offer['market_sku'] for offer in offers if offer['market_sku'] > 0])
        offers_prices = await self._get_offers_prices_by_identifiers(offers_identifiers)
        offers_turnovers = {}
        # try:
        #     async for turnover in self.get_turnover(
        #         [identification.offer_id for identification in offers_identifiers]
        #     ):
        #         offers_turnovers.update(turnover)
        # except DeadlineExceededError:
        #     parser_logger.error(
        #         f"Method {inspect.currentframe().f_code.co_name} "
        #         "canceled by timeout policy"
        #     )
        #     offers_turnovers = {
        #         identification.offer_id: (None, None)
        #         for identification in offers_identifiers
        #     }

        product_ids = {ident.offer_id: ident.product_id for ident in offers_identifiers}

        # Не заменять, опасно!
        # Проверь, где используется
        turnover_default = {
            "hours": -3.0
        }

        for offer in offers:
            attrs = offers_attributes.get(offer['sku'])
            prices = offers_prices.get(offer['sku'], {})
            turnovers = offers_turnovers.get(
                offer['sku'], (
                    turnover_default, turnover_default
                )
            )

            offer.update(attrs)
            offer['name_of_shop'] = self.shop_name
            offer['fbo'] = prices.get('commissions', None)
            offer['your_promotion_price'] = prices.get('marketing_seller_price', None)
            offer['content_rating'] = offers_content_rating.get(offer['market_sku'], None)
            # артикул - product_id
            offer['vendor_code'] = product_ids.get(offer['sku'], None)
            offer.pop('market_sku', None)
            offer['photo'] = offer['photo'][0] if len(offer['photo']) > 0 else None
            offer['turnover_avg_balance'] = turnovers[0]
            offer['turnover_curr_balance'] = turnovers[1]

        return [APIOffer(**i) for i in offers]

    async def get_stocks(self) -> list[APIWarehouse]:
        warehouse_stocks = await self._get_stock_on_warehouses()
        offer_ids = await self._market_sku_to_offer_id()
        temp: dict[str, dict] = dict()

        for warehouse_stock in warehouse_stocks:
            if warehouse_stock['market_sku'] not in offer_ids:
                continue

            stock = APIWarehouseOffer(
                name_of_shop=self.shop_name,
                sku=offer_ids[warehouse_stock['market_sku']],
                current_stock=warehouse_stock['value']
            )

            if warehouse_stock['warehouse_name'] not in temp:
                temp[warehouse_stock['warehouse_name']] = {
                    'name': warehouse_stock['warehouse_name'],
                    'market': 'ozon',
                    'offers': [stock]
                }
            else:
                temp[warehouse_stock['warehouse_name']]['offers'].append(stock)
        result = [APIWarehouse(**i) for i in temp.values()]
        result.extend(await self._get_clusters_info())
        result.append(APIWarehouse(market='ozon', name='!Кластер все магазины', offers=[], warehouse_type=WarehouseType.SUPER_CLUSTER))
        return result

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        chunk_size = 1000

        valid_price_data = [i for i in data if
                            all((i.is_valid_target_price(), i.is_valid_discount_base_price()))]
        invalid_data_length = len(data) - len(valid_price_data)

        if invalid_data_length > 0:
            parser_logger.warning(f'Invalid prices data: {invalid_data_length} / {len(data)}')

        if not valid_price_data:
            parser_logger.warning(f'{self.shop_name}(ozon) has no valid price_data data')
            return

        for i in range(0, len(valid_price_data), chunk_size):
            post_data = []
            for price_data in valid_price_data[i:i + chunk_size]:
                data = {
                    'offer_id': price_data.sku,
                    'currency_code': 'RUB',
                    'auto_action_enabled': 'ENABLED' if price_data.auto_participation_in_promotions else 'DISABLED',
                    'min_price_for_auto_actions_enabled': True if price_data.auto_participation_in_promotions else False,
                    'auto_add_to_ozon_actions_list_enabled': 'ENABLED' if price_data.auto_participation_in_promotions else 'DISABLED',
                    'price_strategy_enabled': 'UNKNOWN',
                    'old_price': str(round(price_data.discount_base_price)),
                    'price': str(price_data.target_price)
                }
                if price_data.min_price is not None:
                    data['min_price'] = price_data.min_price
                post_data.append(data)
            body = {
                'prices': post_data
            }

            response = await self.request(
                'POST',
                url='https://api-seller.ozon.ru/v1/product/import/prices',
                headers=self.auth_headers,
                body=body,
                include_response_logs=True
            )

            await self._get_resp_body_json(response, body=body)

            if not response.ok:
                parser_logger.error(f'Cant change price: {response.reason}: {await response.json()}')
            else:
                for offer_result in (await response.json())['result']:
                    if not offer_result['updated']:
                        parser_logger.warning(
                            f'Error in update offer with id - {offer_result["offer_id"]} \nErrors: {offer_result["errors"]}')

        parser_logger.info(f'{self.shop_name}(ozon) price updated')

    async def _get_offers_identifiers_by_chunks(self) -> AsyncGenerator[list[OfferIdentifier], None]:
        last_id = None
        while True:

            body = {'filter': {},
                    'limit': 1000}
            if last_id is not None:
                body['last_id'] = last_id

            response = await self.request(
                method='POST',
                url='https://api-seller.ozon.ru/v3/product/list',
                headers=self.auth_headers,
                body=body
            )
            await asyncio.sleep(1)
            data = (await self._get_resp_body_json(response))

            data = data['result']
            items = data['items']

            if len(items) == 0:
                return
            yield [OfferIdentifier(product_id=offer['product_id'], offer_id=offer['offer_id']) for offer in items]

            last_id = data['last_id']

    async def _get_offers_base_info(self, offer_data: list[OfferIdentifier]) -> list[dict[str, Any]]:
        chunk_size = 1000
        result = []

        for i in range(0, len(offer_data), chunk_size):
            chunk_offer_ids = [offer.offer_id for offer in offer_data[i:i + chunk_size]]
            body = {
                'offer_id': chunk_offer_ids
            }
            response = await self.request(
                'POST',
                url='https://api-seller.ozon.ru/v3/product/info/list',
                headers=self.auth_headers,
                body=body
            )

            data = await self._get_resp_body_json(response, body=body)
            for offer in data['items']:
                offer_status = offer.get('statuses', {})
                if offer_status.get('validation_status', 'fail') == 'fail' or offer_status.get('status_failed', '') != '':
                    parser_logger.warning(f'Error in offer {offer["offer_id"]} data. Status: {offer_status}')
                try:
                    price_indexes = offer.get('price_indexes', None)

                    external_index_data = price_indexes.get('external_index_data',
                                                            None) if price_indexes is not None else None
                    minimal_price = external_index_data.get('minimal_price',
                                                            None) if external_index_data is not None else None

                    # TODO: Надо починить, смотри старую ручку Озона,
                    #  логика стала другой
                    price_index = price_indexes.get('price_index', None) if price_indexes is not None else None
                    min_market_price = (
                        self._str_to_float(offer['ozon_index_price']['minimal_price'])
                        if offer.get('ozon_index_price', None) is not None
                        else None
                    )

                    result.append({
                        'sku': offer['offer_id'],
                        'name': offer['name'],
                        'photo': offer['primary_image'],
                        'current_price': self._str_to_float(offer['price']),
                        'turnover_curr_balance': min_market_price,
                        'min_price_without_market': self._str_to_float(minimal_price),
                        'attractive_price_threshold': None,
                        'market': 'ozon',
                        'barcodes': ', '.join(offer.get('barcodes', [])),
                        'price_index': self._translate_price_index(price_index),
                        'market_sku': offer['sources'][0]['sku'],
                        'your_price_for_buyers': self._str_to_float(offer['price'])
                    })

                except Exception:
                    parser_logger.error(f'Error in get base info for offer with sku {offer["offer_id"]}', exc_info=True)
        return result

    async def _get_offers_attributes(self, offer_data: list[OfferIdentifier]) -> dict[str, dict[str, Any]]:
        chunk_size = 1000

        result = dict()

        for i in range(0, len(offer_data), chunk_size):
            chunk_offer_ids = [offer.offer_id for offer in offer_data[i:i + chunk_size]]
            body = {
                'filter': {
                    'offer_id': chunk_offer_ids
                },
                'limit': chunk_size
            }

            response = await self.request(
                'POST',
                url='https://api-seller.ozon.ru/v4/product/info/attributes',
                headers=self.auth_headers,
                body=body
            )

            data = await self._get_resp_body_json(response, body=body)
            for offer in data['result']:
                description_attributes = [i['values'][0] for i in offer['attributes'] if
                                          i['id'] == 4191 and len(i['values'])]
                descriptions = html_to_md_linear('. '.join(i['value'] for i in description_attributes))


                unit_dimension_divider = 1
                if offer['dimension_unit'] == 'mm':
                    unit_dimension_divider = 10
                elif offer['dimension_unit'] == 'cm':
                    unit_dimension_divider = 1

                search_attributes = [i for i in offer['attributes'] if i['id'] == 22336]
                search_words = ' #'.join(
                    [' #'.join([words['value'] for words in item['values']]) for item in search_attributes])
                if len(search_words) > 255:
                    search_words = search_words[:search_words[:256].rfind('#')]

                result[offer['offer_id']] = {
                    'self_height': offer['height'] / unit_dimension_divider if offer['height'] else offer['height'],
                    'self_length': offer['depth'] / unit_dimension_divider if offer['depth'] else offer['depth'],
                    'self_width': offer['width'] / unit_dimension_divider if offer['width'] else offer['width'],
                    'self_weight': offer['weight'] / 1000 if offer['weight'] else offer['weight'],
                    'search_words': search_words,
                    'description': descriptions
                }

        return result

    @staticmethod
    def _str_to_float(value: str):
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _translate_price_index(value: str) -> str | None:
        samples = {
            "WITHOUT_INDEX": 'Без индекса',
            "PROFIT": 'Выгодный',
            "AVG_PROFIT": 'Умеренный',
            "NON_PROFIT": 'Невыгодный'
        }
        return samples.get(value, None)

    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        url = 'https://api-seller.ozon.ru/v2/posting/fbo/list'
        body = {
            "dir": "ASC",
            "filter": {
                "since": from_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "status": "delivered",
                "to": to_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            },
            "limit": 1000,
            "offset": 0,
            "translit": True,
            "with": {
                "analytics_data": True,
                "financial_data": True
            }
        }
        response = await self.request('POST', url=url, headers=self.auth_headers, body=body)

        if not response.ok:
            parser_logger.error(f'Cant get orders from {from_date}: {response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                f'Не удалось получить заказы: {response.json().get("message", "unknown")}')

        json_response = await self._get_resp_body_json(response)
        result = []

        for order in json_response.get('result', []):
            if order['status'] == 'cancelled':
                continue

            analytics_data = order.get('analytics_data')

            for order_item in order.get('products', []):
                order_item_data = APIOrderData(
                    internal_order_id=str(order['order_id']),
                    created_at=order.get('created_at'),
                    updated_at=order.get('in_process_at', None),
                    sku=order_item.get('offer_id'),
                    market='ozon',
                    name_of_shop=self.shop_name,
                    quantity=order_item.get('quantity'),
                    price=order_item.get('price', None),
                    warehouse_name=analytics_data.get('warehouse_name').replace('_', ' ').replace('-', ' ').title()
                )
                result.append(order_item_data)

        return result

    @retry(
        retry=retry_if_exception(ApiGateway._is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_random(0, 1),
        reraise=True
    )
    @rate_limiter_gen(secs=61)
    async def get_turnover(
            self,
            skus: list[str],
            size: int | None = None,
            batch_size: int | None = 1000,
    ) -> AsyncIterator[dict[str, tuple[dict, dict]]]:
        """ Возвращает информацию об оборачиваемости остатков """
        if batch_size > 1000:
            raise ValueError("parameter \"batch_size\" must be less than or equal to 1000.")
        if size and size < 0:
            raise ValueError("parameter \"size\" must be positive number.")

        if not skus:
            return

        offset = 0
        while True:
            # формирование запроса
            if size:
                current_batch_size = min(batch_size, size - offset)
            else:
                current_batch_size = min(batch_size, len(skus) - offset)

            if current_batch_size < 1:
                return
            current_batch = skus[offset:offset + current_batch_size]
            offset += current_batch_size

            url = 'https://api-seller.ozon.ru/v1/analytics/turnover/stocks'
            body = {
                "sku": current_batch,
            }

            # отправка запроса
            response = await self.request('POST', url=url, headers=self.auth_headers, body=body)
            try:
                await self._validate_response(response)
            except RequestException as e:
                err_msg = f'Cant get turnover that starts with sku={skus[0]}: {str(e)}'
                parser_logger.critical(err_msg)
                raise MarketplaceAPIException(api_type=str(ApiTypes.OZON), details=err_msg)

            # обработка ответа
            result_batch: dict[str, tuple[dict, dict]] = {}

            resp_body = await response.json()
            for item in resp_body["items"]:
                turnover = item.get('turnover', -3.0)
                idc = item.get('idc', -3.0)

                result_batch[item["sku"]] = (
                    {
                        "days": turnover
                    } if turnover != -3.0
                    else {
                        "hours": turnover
                    },
                    {
                        "days": idc
                    } if idc != -3.0
                    else {
                        "hours": idc
                    },
                )
            yield result_batch

async def main():
    async with get_api_session() as session:
        api = OzonApi(
            token="1eb50510-54a8-409c-a727-9a0d5f24387a",
            entity_id="532844",
            shop_name="SkrabPlus",
            session=session
        )
        async for batch in await api.get_turnover([
            "20068", "20069"
        ]):
            print(batch)

if __name__ == '__main__':
    asyncio.run(main())