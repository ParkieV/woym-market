import asyncio
from io import BytesIO
from typing import Any
from fastapi import HTTPException, status
from requests import Session
import openpyxl
from logs import get_logger
from src.services.stocks_response_handlers import StocksResponseHandler, OFFERS, WAREHOUSES
import pandas as pd
import numpy as np
from src.api.base_api import BaseAPI
from src.schemas.base_api_schemas import APIOffer, APIWarehouseOffer, APIWarehouse, APIPriceChangeData


logger = get_logger(__name__)


class YandexMarketAPI(BaseAPI):
    def validate_auth_data(self, token: str):
        response = self.session.get('https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)
        if response.status_code != 200:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Некорректные данные для инициализации API Яндекс маркта")

    def __init__(self, token: str, entity_id: int, shop_name: str):
        self.session = Session()
        self._token = token
        self._entity_id = entity_id  # same as campaign_id
        self._shop_name = shop_name
        self.auth_headers = {
            'Authorization': f'Bearer {self._token}'
        }
        self.validate_auth_data(token)

    def _get_business_id_by_campaign_id(self, campaign_id: int) -> int:
        return self._get_campaigns()[campaign_id]['business_id']

    async def get_offers_list(self) -> list[APIOffer]:
        result = []
        business_id = self._get_business_id_by_campaign_id(self._entity_id)
        stocks = self._get_offers_stocks(self._entity_id, OFFERS)
        price_report = await self._get_market_prices_report(business_id)
        base_offers = self._get_campaign_offers(business_id)
        # offers_prices = self._get_offers_prices(self._entity_id, [i['sku'] for i in base_offers])

        for offer in base_offers:
            report_line = price_report.get(offer['sku'], {})

            extended_offer = {
                'attractive_price_threshold': report_line.get('attractive_price_threshold', 0),
                'moderately_attractive_price_threshold': report_line.get('moderately_attractive_price_threshold', 0),
                'best_place_wm': report_line.get('best_place_wm', ''),
                'min_price_without_market': report_line.get('min_price_without_market', 0),
                'best_place_im': report_line.get('best_place_im', ''),
                'min_price_in_market': report_line.get('min_price_in_market', 0),
                'min_general_markets_price': report_line.get('min_general_markets_price', 0),
                'your_price_for_buyers': report_line.get('your_price_for_buyers', 0),
                'group_sellers_amount': 0,
                'remaining_stock': stocks.get(offer['sku'], 0),
                'name_of_shop': self._shop_name,
                'best_place_im_link': report_line.get('best_place_im_link', None),
                'fbo': None
                # 'current_price': offers_prices.get(offer['sku'], None)
            }
            extended_offer.update(offer)
            result.append(extended_offer)

        logger.info('Yandex offers collected')
        return [APIOffer(**offer) for offer in result]

    def _get_campaigns(self) -> dict[int, dict[str, Any]]:
        response = self.session.get('https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)

        self.validate_response(response)

        data = response.json()

        return {campaign['id']: {'business_id': campaign['business']['id'], 'name': campaign['business']['name']} for
                campaign in data['campaigns']}

    def _get_offers_stocks(self, campaign_id: int, handler: StocksResponseHandler = OFFERS):
        warehouses = []
        page_token = ''
        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/stocks?page_token={page_token}',
                headers=self.auth_headers
            )
            self.validate_response(response)
            data = response.json()
            warehouses.extend(data['result']['warehouses'])

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break

        result = handler(warehouses)
        return result

    def _get_campaign_offers(self, business_id: int) -> list[dict]:
        results = []
        page_token = ''
        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings?limit=200&page_token={page_token}',
                headers=self.auth_headers
            )

            self.validate_response(response)
            data = response.json()

            for offer in data['result']['offerMappings']:
                offer = offer['offer']

                if 'weightDimensions' in offer:
                    weight_dimensions = offer['weightDimensions']
                    volume = weight_dimensions['width'] * weight_dimensions['length'] * weight_dimensions['height'] / 1000
                else:
                    weight_dimensions = dict()
                    volume = None

                offer_data = {
                    'sku': offer['offerId'],
                    'name': offer['name'],
                    'yandex_weight': weight_dimensions.get('weight'),
                    'yandex_length': weight_dimensions.get('length'),
                    'yandex_width': weight_dimensions.get('width'),
                    'yandex_height': weight_dimensions.get('height'),
                    'yandex_volume': volume,
                    'photo': offer['pictures'][0] if len(offer['pictures']) > 0 else None,
                    'current_price': offer['basicPrice']['value'] if 'basicPrice' in offer else None,
                    'business_id': business_id,
                    'barcodes': ', '.join(offer['barcodes']) if offer['barcodes'] else None

                }
                offer_data['your_promotion_price'] = offer_data['current_price']
                results.append(offer_data)

            page_token = data['result']['paging'].get('nextPageToken', None)

            if page_token is None:
                break

        return results

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        chunk_size = 500

        business_id = self._get_business_id_by_campaign_id(self._entity_id)

        for i in range(0, len(data), chunk_size):
            post_data = [
                {
                    'offerId': price_data.sku,
                    'price': {
                        'value': price_data.target_price,
                        'currencyId': "RUR"
                    }
                }
                for price_data in data[i:i + chunk_size] if price_data.is_valid_data()]

            if not post_data:
                continue

            body = {
                'offers': post_data
            }

            response = self.session.post(
                        f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-prices/updates',
                        headers=self.auth_headers,
                        json=body
                    )
            self.validate_response(response, body=body, raise_error=False)

        self._set_cofinance_offers_price(data)

        logger.info('Yandex prices updated')

    async def _get_market_prices_report(self, business_id: int) -> dict[str, dict[str, Any]]:
        response = self.session.post('https://api.partner.market.yandex.ru/reports/prices/generate',
                                     json={'businessId': business_id}, headers=self.auth_headers)

        self.validate_response(response)

        data = response.json()
        report_id = data['result']['reportId']

        while True:
            response = self.session.get(f'https://api.partner.market.yandex.ru/reports/info/{report_id}',
                                        headers=self.auth_headers)
            data = response.json()
            if data['result']['status'] == 'DONE':

                output = BytesIO()
                response = self.session.get(data['result']['file'])
                output.write(response.content)

                wb = openpyxl.load_workbook(output)
                ws = wb.active
                links = [row[16].hyperlink.target if row[16].hyperlink else None for row in ws.rows]
                links_series = pd.Series(links)[1:].reset_index(drop=True)

                df = self._download_report(data['result']['file'])
                df.drop([0, 1, 2, 3], inplace=True)
                new_df = pd.DataFrame()
                new_df[['sku', 'attractive_price_threshold', 'moderately_attractive_price_threshold',
                        'your_price_for_buyers', 'min_general_markets_price', 'best_place_wm',
                        'min_price_without_market', 'best_place_im',
                        'min_price_in_market']] = df.iloc[:, [0, 6, 7, 10, 13, 14, 15, 16, 17]]
                new_df.replace({'–': np.nan}, inplace=True)
                new_df['best_place_im_link'] = links_series
                new_df[['best_place_wm', 'best_place_im']] = new_df[['best_place_wm', 'best_place_im']].fillna('')

                result = new_df.to_dict('records')
                result = {
                    i['sku']: {
                        'attractive_price_threshold': i['attractive_price_threshold'],
                        'moderately_attractive_price_threshold': i['moderately_attractive_price_threshold'],
                        'min_general_markets_price': i['min_general_markets_price'],
                        'best_place_wm': i['best_place_wm'],
                        'min_price_without_market': i['min_price_without_market'],
                        'best_place_im': str(i['best_place_im']).replace(' • FBY', '').replace(' • FBS', ''),
                        'min_price_in_market': i['min_price_in_market'],
                        'your_price_for_buyers': i['your_price_for_buyers'],
                        'best_place_im_link': i['best_place_im_link']
                    }
                    for i in result
                }

                # get hyperlinks to best market price

                return result

            elif data['result']['status'] == 'FAILED':
                self._raise_error(response.reason, response.status_code)

            await asyncio.sleep(5)

    async def get_stocks(self) -> list[APIWarehouse]:
        result = []

        warehouses = self._get_warehouses_info()
        offers_stocks = self._get_offers_stocks(self._entity_id, WAREHOUSES)

        for warehouse_id in warehouses.keys():
            offers = [
                APIWarehouseOffer(
                    sku=offer['offerId'],
                    name_of_shop=self._shop_name,
                    current_stock=sum([i['count'] for i in offer['stocks'] if i['type'] == 'AVAILABLE'])
                )
                for offer in offers_stocks[warehouse_id]
            ]

            warehouse = APIWarehouse(
                market='yandex',
                offers=offers,
                name=warehouses[warehouse_id]['name'],
            )
            result.append(warehouse)
        return result

    def _get_warehouses_info(self) -> dict[int, dict[str, Any]]:
        response = self.session.get(f'https://api.partner.market.yandex.ru/warehouses', headers=self.auth_headers)
        self.validate_response(response, raise_error=True)

        data = response.json()

        result = dict()
        for warehouse in data['result']['warehouses']:
            result[warehouse['id']] = {
                'name': warehouse['name']
            }

        return result

    def _get_offers_price(self, campaign_id: int) -> dict[str, float]:
        page_token = ''
        result = dict()

        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offer-prices?page_token={page_token}',
                headers=self.auth_headers)
            self.validate_response(response)

            data = response.json()

            for offer_data in data['offers']:
                result[data['offerId']] = data['offerId']['price']['value']

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break

        return result

    def _get_offers_prices(self, campaign_id: int, skus: list[str]) -> dict[str, int]:
        chunk_size = 80
        result = dict()

        for i in range(0, len(skus), chunk_size):
            body = {
                "offerIds": skus[i:i+chunk_size],
            }
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offer-prices',
                headers=self.auth_headers,
                json=body
            )
            self.validate_response(response)
            data = response.json()

            for offer_price_info in data['result']['offers']:
                if 'price' not in offer_price_info or 'value' not in offer_price_info['price']:
                    continue

                result[offer_price_info['offerId']] = offer_price_info['price']['value']

        return result

    def _set_cofinance_offers_price(self, data: list[APIPriceChangeData]):
        chunk_size = 500
        business_id = self._get_business_id_by_campaign_id(self._entity_id)
        valid_data = [i for i in data if i.auto_min_price is not None and i.auto_min_price != np.nan]

        for i in range(0, len(data), chunk_size):

            body = {
                'offerMappings': [
                    {
                        'offer': {
                            'offerId': price_data.sku,
                            'cofinancePrice': {
                                'value': int(price_data.auto_min_price),
                                'currencyId': 'RUR'
                            }
                        }
                    }
                    for price_data in valid_data[i:i+chunk_size]
                ]
            }

            response = self.session.post(
                f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings/update',
                headers=self.auth_headers,
                json=body
            )
            self.validate_response(response, raise_error=False, body=body)

