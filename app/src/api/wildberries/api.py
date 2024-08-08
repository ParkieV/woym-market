from requests import Session

from logs import get_logger
from src.api.base_api import BaseAPI
from src.schemas.base_api_schemas import APIPriceChangeData, APIWarehouse, APIOffer, WarehouseType

logger = get_logger(__name__)


class WildberriesAPI(BaseAPI):

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


    async def get_offers_list(self) -> list[APIOffer]:
        pass

    async def get_stocks(self) -> list[APIWarehouse]:
        pass

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        pass

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
                offer = {
                    'sku': item['vendorCode'],
                    'name': item['title'],
                    'name_of_shop': self.shop_name,
                    'yandex_length': item['dimensions']['length'],
                    'yandex_width': item['dimensions']['width'],
                    'yandex_height': item['dimensions']['height'],
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

    def _get_warehouse(self):
        url = 'https://marketplace-api.wildberries.ru/api/v3/offices'
        result = []
        response = self.session.get(url, headers=self.auth_headers)

        if not response.ok:
            # TODO
            return

        response_data = response.json()

        for item in response_data:
            result.append(APIWarehouse(
                market='wildberries',
                name=item['name'],
                warehouse_type=WarehouseType.WAREHOUSE,
                offers=[]
            ))

        return result
