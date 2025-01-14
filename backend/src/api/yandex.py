import asyncio
from collections import defaultdict
from collections.abc import AsyncGenerator
from math import ceil
from io import BytesIO
from typing import Any

from aiohttp import ClientSession, ClientResponse

from logs import get_logger
from datetime import datetime, timedelta

import openpyxl
import numpy as np
import pandas as pd
from fastapi import HTTPException, status

from src.api.exceptions import InitializationError, RequestException
from src.api.gateway_template import ApiGateway
from src.api.interfaces import IApiGateway, ApiTypes
from src.services.stocks_response_handlers import StocksResponseHandler, OFFERS, WAREHOUSES
from src.schemas.base_api_schemas import APIOffer, APIWarehouseOffer, APIWarehouse, APIPriceChangeData, \
    APIOfferChangeData, APIOrderData, WarehouseType

logger = get_logger(__name__, tags={'marketplace_api': 'yandex'})


class YandexMarketApi(ApiGateway, IApiGateway):
    market_type = 'Yandex'

    async def validate_auth_data(self):
        response = await self.request('GET', url='https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)
        if response.status != 200:
            raise InitializationError(ApiTypes.YANDEX, "Incorrect token")

    def __init__(self, token: str, entity_id: str | None, shop_name: str, session: ClientSession): #type: ignore
        try:
            super().__init__(token, entity_id, shop_name, session)
        except InitializationError as err:
            raise InitializationError(ApiTypes.YANDEX, err.detail)

        self.auth_headers = {
            'Api-Key': self.token
        }
        asyncio.create_task(self.validate_auth_data())

    async def _get_business_id_by_campaign_id(self, campaign_id: str) -> int:
        try:
            data = await self._get_campaigns()
        except Exception as err:
            raise err
        return data[campaign_id]['business_id']

    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        check_valid = lambda x: all((x.is_valid_name(), x.is_valid_description(), x.is_valid_barcodes(), x.is_valid_sizes()))
        valida_offer_data = [i for i in data if check_valid(i)]
        invalid_offer_data = [i for i in data if not check_valid(i)]

        if invalid_offer_data:
            logger.warning(
                f'Invalid offers data: {len(invalid_offer_data)} / {len(valida_offer_data)} {invalid_offer_data}')

        business_id = await self._get_business_id_by_campaign_id(self.client_id)
        url = f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings/update'

        chunk_size = 500

        for i in range(0, len(valida_offer_data), chunk_size):
            body = {
                'offerMappings': [
                    {
                        'offer': {
                            'offerId': offer_data.sku,
                            'barcodes': [barcode for barcode in offer_data.valid_barcodes],
                            'name': offer_data.name,
                            'description': offer_data.description,
                            'weightDimensions': {
                                'length': ceil(offer_data.self_length),
                                'width': ceil(offer_data.self_width),
                                'height': ceil(offer_data.self_height),
                                'weight': offer_data.self_weight,
                            }

                        }
                    }
                    for offer_data in valida_offer_data[i:i + chunk_size]
                ]
            }
            response = await self.request('POST', url=url, body=body, headers=self.auth_headers, include_response_logs=True)

            if not response.ok:
                logger.error(f'Cant update offers data: {response.text}')

            response_json = await self.validate_response(response)

            if not response.ok:
                logger.error(f'Cant update offers data: {response_json.get("errors", "unknown")}')

    async def validate_response(self, response: ClientResponse, body: Any = None) -> Any:
        data_json = await response.json()

        if response.status != 200 :
            raise RequestException(f'status: {response.status} \ndetail: {data_json}')

        return data_json

    async def get_offers_list(self) -> list[APIOffer]:
        result = []
        business_id = await self._get_business_id_by_campaign_id(self.client_id)
        # stocks = self._get_offers_stocks(self.client_id, OFFERS)
        price_report = await self._get_market_prices_report(business_id)
        base_offers = []
        async for chunk in self._get_campaign_offers(business_id):
            base_offers += chunk
        # offers_prices = self._get_offers_prices(self.client_id, [i['sku'] for i in base_offers])

        for offer in base_offers:
            report_line = price_report.get(offer['sku'], {})

            extended_offer = {
                'attractive_price_threshold': _ if (_ := report_line.get('attractive_price_threshold', 0)) else 0,
                'moderately_attractive_price_threshold': _ if (_ := report_line.get('moderately_attractive_price_threshold', 0)) else 0,
                'best_place_wm': _ if (_ := report_line.get('best_place_wm', '')) is not None else '',
                'min_price_without_market': _ if (_ := report_line.get('min_price_without_market', 0)) else 0,
                'best_place_im': report_line.get('best_place_im', ''),
                'min_price_in_market': _ if (_ := report_line.get('min_price_in_market', 0)) else 0,
                'min_general_markets_price': _ if (_ := report_line.get('min_general_markets_price', 0)) else 0,
                'your_price_for_buyers': _ if (_ := report_line.get('your_price_for_buyers', 0)) else 0,
                'group_sellers_amount': 0,
                'name_of_shop': self.shop_name,
                'best_place_im_link': _ if (_ := report_line.get('best_place_im_link', '')) else '',
                'fbo': None
                # 'current_price': offers_prices.get(offer['sku'], None)
            }
            extended_offer.update(offer)
            result.append(extended_offer)

        return [APIOffer(**offer) for offer in result]

    async def _get_campaigns(self) -> dict[str, dict[str, Any]]:
        """ Получить магазины, доступные по данному токену"""
        response = await self.request('GET', url='https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)

        data = await self.validate_response(response)

        return {str(campaign['id']): {'business_id': campaign['business']['id'], 'name': campaign['business']['name']} for
                campaign in data['campaigns']}

    async def _get_offers_stocks(self, campaign_id: str, handler: StocksResponseHandler = OFFERS) -> defaultdict:
        warehouses = []
        page_token = ''
        while True:
            response = await self.request(
                'POST',
                url=f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/stocks?page_token={page_token}',
                headers=self.auth_headers
            )
            data = await self.validate_response(response)
            warehouses.extend(data['result']['warehouses'])

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break

        result = handler(warehouses)
        return result

    async def _get_campaign_offers(self, business_id: int) -> AsyncGenerator[list[str, Any]]:
        """ Получить информацию о товарах в каталоге """
        page_token = None
        chunk_size = 200

        while True:
            base_url = f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings?limit={chunk_size}'
            if page_token is not None:
                base_url += f'&page_token={page_token}'
            response = await self.request(
                method='POST',
                url=base_url,
                headers=self.auth_headers
            )

            data = await self.validate_response(response)

            offer_chunk = data['result']['offerMappings']

            if len(offer_chunk) == 0:
                return

            validated_offer_chunk = []
            for offer_mapping in offer_chunk:
                offer = offer_mapping['offer']
                mapping = offer_mapping.get('mapping', {})

                if 'weightDimensions' in offer:
                    weight_dimensions = offer['weightDimensions']
                    volume = weight_dimensions['width'] * weight_dimensions['length'] * weight_dimensions[
                        'height'] / 1000
                else:
                    weight_dimensions = dict()
                    volume = None

                offer_data = {
                    'sku': offer['offerId'],
                    'name': offer['name'],
                    'description': offer.get('description', None),
                    'self_weight': weight_dimensions.get('weight'),
                    'self_length': ceil(weight_dimensions.get('length')) if weight_dimensions.get('length') else None,
                    'self_width': ceil(weight_dimensions.get('width')) if weight_dimensions.get('width') else None,
                    'self_height': ceil(weight_dimensions.get('height')) if weight_dimensions.get('height') else None,
                    'volume': volume,
                    'photo': offer['pictures'][0] if len(offer['pictures']) > 0 else None,
                    'current_price': offer['basicPrice']['value'] if 'basicPrice' in offer else None,
                    'business_id': business_id,
                    'barcodes': ', '.join(offer['barcodes']) if offer['barcodes'] else None,
                    'vendor_code': mapping.get('marketSku', None)

                }
                offer_data['your_promotion_price'] = offer_data['current_price']
                validated_offer_chunk.append(offer_data)

            yield validated_offer_chunk

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                return

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        chunk_size = 500

        valid_price_data = [i for i in data if i.is_valid_target_price() and i.is_valid_discount_base_price()]
        invalid_price_data = [i for i in data if not (i.is_valid_target_price() and i.is_valid_discount_base_price())]

        if invalid_price_data:
            logger.warning(
                f'Invalid prices data: {len(invalid_price_data)} / {len(valid_price_data)} {invalid_price_data}')

        if not valid_price_data:
            logger.warning(f'{self.shop_name}(yandex) has no valid price data')
            return

        business_id = await self._get_business_id_by_campaign_id(self.client_id)

        for i in range(0, len(valid_price_data), chunk_size):
            post_data = [
                {
                    'offerId': price_data.sku,
                    'price': {
                        'value': price_data.target_price,
                        'discountBase': round(price_data.discount_base_price),
                        'currencyId': "RUR"
                    }
                }
                for price_data in valid_price_data[i:i + chunk_size]]

            body = {
                'offers': post_data
            }

            response = await self.request(
                'POST',
                url=f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-prices/updates',
                headers=self.auth_headers,
                body=body,
                include_response_logs=True
            )
            if not response.ok:
                logger.error(f'{self.shop_name}(yandex) has invalid price data: {response.text}')

        await self._set_cofinance_offers_price(data)

        logger.info(f'{self.shop_name}(yandex) prices updated: {len(valid_price_data)} of {len(data)}')

    async def _get_market_prices_report(self, business_id: int) -> dict[str, dict[str, Any]]:
        response = await self.request('POST', url='https://api.partner.market.yandex.ru/reports/prices/generate', body={'businessId': business_id}, headers=self.auth_headers)

        data = await self.validate_response(response)

        report_id = data['result']['reportId']

        while True:
            response = await self.request('GET', url=f'https://api.partner.market.yandex.ru/reports/info/{report_id}',
                                        headers=self.auth_headers)
            data = await self.validate_response(response)
            if data['result']['status'] == 'DONE':

                output = BytesIO()
                response = await self.request('GET', url=data['result']['file'])
                output.write(await response.read())

                wb = openpyxl.load_workbook(output)
                ws = wb.active
                links = [row[16].hyperlink.target if row[16].hyperlink else None for row in ws.rows]
                links_series = pd.Series(links)[1:].reset_index(drop=True)

                df = await self._download_report(data['result']['file'])
                df.drop([0, 1, 2, 3], inplace=True)
                new_df = pd.DataFrame()
                new_df[['sku', 'attractive_price_threshold', 'moderately_attractive_price_threshold',
                        'your_price_for_buyers', 'min_general_markets_price', 'best_place_wm',
                        'min_price_without_market', 'best_place_im',
                        'min_price_in_market']] = df.iloc[:, [0, 3, 4, 6, 11, 12, 13, 14, 15]]
                new_df.replace({'–': np.nan}, inplace=True)
                new_df['best_place_im_link'] = links_series
                new_df[['best_place_wm', 'best_place_im']] = new_df[['best_place_wm', 'best_place_im']].fillna('')

                result = new_df.to_dict('records')

                result = {
                    i['sku']: {
                        'attractive_price_threshold': None
                                                        if (_ := i.get('attractive_price_threshold')) or _ == np.nan
                                                        else i['attractive_price_threshold'],
                        'moderately_attractive_price_threshold': None
                                                        if (_ := i.get('moderately_attractive_price_threshold')) or _ == np.nan
                                                        else i['moderately_attractive_price_threshold'],
                        'min_general_markets_price': None
                                                        if (_ := i.get('min_general_markets_price')) or _ == np.nan
                                                        else i['min_general_markets_price'],
                        'best_place_wm': None
                                            if (_ := i.get('best_place_wm')) or _ == np.nan
                                            else i['best_place_wm'],
                        'min_price_without_market': None
                                                    if (_ := i.get('min_price_without_market')) or _ == np.nan
                                                    else i['min_price_without_market'],
                        'best_place_im': str(i['best_place_im']).replace(' • FBY', '').replace(' • FBS', ''),
                        'min_price_in_market': None
                                                if (_ := i.get('min_price_in_market')) or _ == np.nan
                                                else i['min_price_in_market'],
                        'your_price_for_buyers': None
                                                    if (_ := i.get('your_price_for_buyers')) or _ == np.nan
                                                    else i['your_price_for_buyers'],
                        'best_place_im_link': None
                                                if (_ := i.get('best_place_im_link')) or _ == np.nan
                                                else i['best_place_im_link'],
                    }
                    for i in result
                }
                # get hyperlinks to best market price

                return result

            elif data['result']['status'] == 'FAILED':
                raise RequestException(f'status: {response.status} \ndetail: {response.reason}')

            await asyncio.sleep(5)

    async def get_stocks(self) -> list[APIWarehouse]:
        result = []

        warehouses = await self._get_warehouses_info()
        offers_stocks = await self._get_offers_stocks(self.client_id, WAREHOUSES)

        for warehouse_id in warehouses.keys():
            offers = [
                APIWarehouseOffer(
                    sku=offer['offerId'],
                    name_of_shop=self.shop_name,
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
        result.append(APIWarehouse(name='Кластер все магазины', offers=[], warehouse_type=WarehouseType.SUPER_CLUSTER, market='yandex'))
        return result

    async def _get_warehouses_info(self) -> dict[int, dict[str, Any]]:
        response = await self.request('GET', url=f'https://api.partner.market.yandex.ru/warehouses', headers=self.auth_headers)
        data = await self.validate_response(response)

        result = dict()
        for warehouse in data['result']['warehouses']:
            result[warehouse['id']] = {
                'name': warehouse['name']
            }

        return result

    async def _get_offers_price(self, campaign_id: int) -> dict[str, float]:
        page_token = ''
        result = dict()

        while True:
            response = await self.request(
                'POST',
                url=f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offer-prices?page_token={page_token}',
                headers=self.auth_headers)
            data = self.validate_response(response)


            for offer_data in data['offers']:
                result[offer_data['offerId']] = offer_data['offerId']['price']['value']

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break

        return result

    async def _get_offers_prices(self, campaign_id: int, skus: list[str]) -> dict[str, int]:
        chunk_size = 80
        result = dict()

        for i in range(0, len(skus), chunk_size):
            body = {
                "offerIds": skus[i:i + chunk_size],
            }
            response = await self.request(
                'POST',
                url=f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offer-prices',
                headers=self.auth_headers,
                body=body
            )
            data = await self.validate_response(response)

            for offer_price_info in data['result']['offers']:
                if 'price' not in offer_price_info or 'value' not in offer_price_info['price']:
                    continue

                result[offer_price_info['offerId']] = offer_price_info['price']['value']

        return result

    async def _set_cofinance_offers_price(self, data: list[APIPriceChangeData]):
        chunk_size = 500
        business_id = await self._get_business_id_by_campaign_id(self.client_id)
        valid_data = [i for i in data if i.is_valid_auto_min_price()]

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
                    for price_data in valid_data[i:i + chunk_size] if price_data.is_valid_auto_min_price()
                ]
            }

            response = await self.request(
                'POST',
                url=f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings/update',
                headers=self.auth_headers,
                body=body
            )
            await self.validate_response(response, body=body)

    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        if (to_date - from_date).days > 30:
            from_date = to_date - timedelta(days=30)

        url = f'https://api.partner.market.yandex.ru/campaigns/{self.client_id}/orders'
        params = {
            'pageSize': 50,
            'page': 1,
            'fake': 'false',
            'fromDate': from_date.strftime('%d-%m-%Y'),
            'toDate': to_date.strftime('%d-%m-%Y'),
        }

        results = []

        while True:
            response = await self.request('GET', url=url, headers=self.auth_headers, params=params)

            if not response.ok:
                logger.error(f'Cant collect orders: {response.text}')
                raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Не удалось получить информацию о заказах')

            json_response = await self.validate_response(response)

            if not json_response['orders']:
                break

            for order in json_response['orders']:
                if order['status'] in ('CANCELLED', 'RETURNED', 'UNKNOWN'):
                    continue

                for order_item in order['items']:
                    created_at = datetime.strptime(order['creationDate'], '%d-%m-%Y %H:%M:%S')
                    updated_at = datetime.strptime(order['updatedAt'], '%d-%m-%Y %H:%M:%S') if order.get('updatedAt',
                                                                                                         None) else None
                    results.append(
                        APIOrderData(
                            internal_order_id=str(order['id']),
                            sku=order_item['offerId'],
                            market='yandex',
                            name_of_shop=self.shop_name,
                            quantity=order_item['count'],
                            created_at=created_at,
                            updated_at=updated_at,
                            price=order_item['price'],
                            warehouse_name=None
                        )
                    )

            params['page'] += 1

        return results
