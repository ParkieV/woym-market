from typing import Any
from requests import Session
from src.api.base_api import BaseAPI
from src.schemas.base_api_schemas import APIOffer, APIWarehouseOffer, APIWarehouse, APIPriceChangeData
from dataclasses import dataclass


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

        for offer in offers:
            attrs = offers_attributes.get(offer['sku'], None)
            offer.update(attrs)
            offer['name_of_shop'] = self.shop_name

        return [APIOffer(**i) for i in offers]

    async def get_stocks(self) -> list[APIWarehouse]:
        # TODO подключить склады и остатки
        return []

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

            self.validate_response(response, raise_error=False, body=body)

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
                result.append({
                    'sku': offer['offer_id'],
                    'name': offer['name'],
                    'photo': offer['primary_image'],
                    'current_price': self.__str_to_float(offer['price']),
                    'remaining_stock': offer['stocks']['present'],
                    'min_price_in_market': self.__str_to_float(offer['min_ozon_price']),
                    'min_price_without_market': self.__str_to_float(offer['price_indexes']['external_index_data']['minimal_price']),
                    'attractive_price_threshold': self.__str_to_float(offer['recommended_price']),
                    'market': 'ozon'
                })

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

    def get_content_ratings(self, skus: list[str]):
        body = {
            'skus': skus
        }
        response = self.session.post('https://api-seller.ozon.ru/v1/product/rating-by-sku', headers=self.auth_headers, json=body)
        data = self.validate_response(response, body=body)
        return {item['sku']: item['rating'] for item in data['products']}
