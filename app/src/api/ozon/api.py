from typing import Any
from requests import Session
from src.api.base_api import BaseAPI
from src.schemas.base_api_schemas import APIOffer, APIWarehouseOffer, APIWarehouse, APIPriceChangeData
from dataclasses import dataclass
from logs import get_logger

logger = get_logger(__name__)


@dataclass
class OfferIdentifier:
    product_id: int
    offer_id: str


class OzonAPI(BaseAPI):
    def __init__(self, token: str, entity_id: int, shop_name: str):
        self.token = token
        self.shop_name = shop_name
        self.client_id = str(entity_id)
        self.auth_headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.token,
        }
        self.session = Session()

    async def validate_auth_data(self, **kwargs):
        pass

    def __str_to_float(self, value):
        if value:
            return float(value)
        return None

    async def get_offers_list(self) -> list[APIOffer]:
        offers_identifiers = self._get_offers_identifiers()
        offers = self._get_offers_base_info(offers_identifiers)
        offers_attributes = self._get_offers_attributes(offers_identifiers)
        offers_content_rating = self._get_content_ratings(
            [offer['market_sku'] for offer in offers if offer['market_sku'] > 0])
        offers_commissions = self._get_offers_commissions(offers_identifiers)

        for offer in offers:
            attrs = offers_attributes.get(offer['sku'], None)
            offer.update(attrs)
            offer['name_of_shop'] = self.shop_name
            offer['fby'] = offers_commissions.get(offer['sku'], None)
            offer['content_rating'] = offers_content_rating.get(offer['market_sku'], None)
            del offer['market_sku']

        logger.info('Ozon offers collected')
        return [APIOffer(**i) for i in offers]

    async def get_stocks(self) -> list[APIWarehouse]:
        warehouse_stocks = self._get_stock_on_warehouses()
        offer_ids = self._market_sku_to_offer_id()
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

        return [APIWarehouse(**i) for i in temp.values()]

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        chunk_size = 1000

        for i in range(0, len(data), chunk_size):
            post_data = [
                {
                    'offer_id': price.sku,
                    'price': str(price.target_price),
                    'currency_code': 'RUB',
                    'auto_action_enabled': 'UNKNOWN',
                    'price_strategy_enabled': 'UNKNOWN',
                    'min_price': str(price.min_price)
                }
                for price in data[i:i + chunk_size]
            ]
            body = {
                'prices': post_data
            }

            response = self.session.post(
                'https://api-seller.ozon.ru/v1/product/import/prices',
                headers=self.auth_headers,
                json=body
            )

            # TODO обработать ошибки
            self.validate_response(response, raise_error=False, body=body)

        logger.info('Ozon price updated')

    def _get_offers_identifiers(self) -> list[OfferIdentifier]:
        response = self.session.post('https://api-seller.ozon.ru/v2/product/list', headers=self.auth_headers)

        data = self.validate_response(response)['result']['items']

        return [OfferIdentifier(product_id=offer['product_id'], offer_id=offer['offer_id']) for offer in data]

    def _get_offers_base_info(self, data: list[OfferIdentifier]) -> list[dict[str, Any]]:
        chunk_size = 1000
        result = []

        for i in range(0, len(data), chunk_size):
            chunk_offer_ids = [offer.offer_id for offer in data[i:i + chunk_size]]
            body = {
                'offer_id': chunk_offer_ids
            }
            response = self.session.post(
                'https://api-seller.ozon.ru/v2/product/info/list',
                headers=self.auth_headers,
                json=body
            )

            data = self.validate_response(response, body=body)

            for offer in data['result']['items']:
                try:
                    result.append({
                        'sku': offer['offer_id'],
                        'name': offer['name'],
                        'photo': offer['primary_image'],
                        'current_price': self.__str_to_float(offer['price']),
                        'remaining_stock': offer['stocks']['present'],
                        'min_price_in_market': self.__str_to_float(offer['min_ozon_price']),
                        'min_price_without_market': self.__str_to_float(
                            offer['price_indexes']['external_index_data']['minimal_price']),
                        'attractive_price_threshold': self.__str_to_float(offer['recommended_price']),
                        'market': 'ozon',
                        'discount_base_price': self.__str_to_float(offer['old_price']),
                        'price_index': self.__translate_price_index(offer['price_indexes']['price_index']),
                        'market_sku': offer['sku']
                    })
                except Exception as e:
                    logger.error(f'Error in get base info for offer with sku {offer["offer_id"]}', exc_info=True)

        return result

    def _get_offers_attributes(self, data: list[OfferIdentifier]) -> dict[str, dict[str, Any]]:
        chunk_size = 1000

        result = dict()

        for i in range(0, len(data), chunk_size):
            chunk_offer_ids = [offer.offer_id for offer in data[i:i + chunk_size]]
            body = {
                'filter': {
                    'offer_id': chunk_offer_ids
                },
                'limit': chunk_size
            }

            response = self.session.post(
                'https://api-seller.ozon.ru/v3/products/info/attributes',
                headers=self.auth_headers,
                json=body
            )

            data = self.validate_response(response, body=body)

            for offer in data['result']:
                # TODO посчитать объем
                result[offer['offer_id']] = {
                    'yandex_height': offer['height'],
                    'yandex_length': offer['depth'],
                    'yandex_width': offer['width'],
                    'yandex_weight': offer['weight'],
                }

        return result

    def __translate_price_index(self, value):
        samples = {
            "WITHOUT_INDEX": 'Без индекса',
            "PROFIT": 'Выгодный',
            "AVG_PROFIT": 'Умеренный',
            "NON_PROFIT": 'Невыгодный'
        }
        return samples.get(value, None)

    def _get_content_ratings(self, skus: list[int]):
        chunk_size = 100
        result = {}

        for i in range(0, len(skus), chunk_size):
            body = {
                'skus': skus[i:i + chunk_size]
            }
            response = self.session.post('https://api-seller.ozon.ru/v1/product/rating-by-sku',
                                         headers=self.auth_headers, json=body)
            data = self.validate_response(response, body=body)
            result.update({item['sku']: item['rating'] for item in data['products']})

        return result

    def _get_stock_on_warehouses(self):
        chunk_size = 1000
        offset = 0
        result = []

        while True:
            body = {
                'limit': chunk_size,
                'offset': offset,
                'warehouse_type': 'ALL'
            }
            response = self.session.post('https://api-seller.ozon.ru/v2/analytics/stock_on_warehouses',
                                         headers=self.auth_headers, json=body)

            data = self.validate_response(response, True, body)

            if not data['result']['rows']:
                break

            for stock in data['result']['rows']:
                stock_data = {
                    'value': stock['free_to_sell_amount'],
                    'market_sku': stock['sku'],
                    'warehouse_name': stock['warehouse_name']
                }
                result.append(stock_data)

            offset += chunk_size

        return result

    def _market_sku_to_offer_id(self) -> dict[int, str]:
        offers_identifiers = self._get_offers_identifiers()
        offers = self._get_offers_base_info(offers_identifiers)

        return {offer['market_sku']: offer['sku'] for offer in offers if offer['market_sku'] != 0}

    def _get_offers_commissions(self, data: list[OfferIdentifier]) -> dict[str, float]:
        chunk_size = 1000
        result = dict()

        for i in range(0, len(data), chunk_size):
            body = {
                'filter': {
                    'offer_id': [i.offer_id for i in data[i:i+chunk_size]]
                },
                'limit': chunk_size
            }
            response = self.session.post('https://api-seller.ozon.ru/v4/product/info/prices', headers=self.auth_headers, json=body)

            data = self.validate_response(response, body=body)

            for offer in data['result']['items']:
                try:
                    commissions = offer['commissions']

                    sales_percent = commissions['sales_percent_fbo']
                    price = self.__str_to_float(offer['price']['price'])

                    expenses = sum([
                        commissions['fbo_return_flow_trans_max_amount'],
                        commissions['fbo_deliv_to_customer_amount'],
                    ])

                    result[offer['offer_id']] = price * sales_percent / 100 + expenses
                except Exception as e:
                    logger.error(f'Error in get commission for offer with sku {offer["offer_id"]}', exc_info=True)

        return result


