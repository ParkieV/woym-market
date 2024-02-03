from dataclasses import asdict
from io import BytesIO
import asyncio
from typing import Any
from fastapi import HTTPException
from requests import Session, Response
from src.schemas.yandex_api_schemas import CampaignInfo, BusinessInfo, YandexOfferInfo, YandexOfferInfoPartial
from enum import Enum
from src.services.stocks_response_handlers import StocksResponseHandler, OFFERS
import pandas as pd
from collections import defaultdict
import numpy as np


class StocksResponseType(Enum):
    OFFERS = 1
    WAREHOUSES = 2
    OFFERS_DETAIL = 3


class YandexMarketAPI:
    def __init__(self, token: str):
        self.session = Session()
        self.token = token
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }

    async def get_offers(self) -> [YandexOfferInfo]:
        result = []

        campaigns = self.get_campaigns()

        for campaign in campaigns:
            stocks = self.get_stocks(campaign.id, OFFERS)
            price_report = await self._get_market_prices_report(campaign.business.id)
            base_offers = self._get_campaign_offers(campaign.business.id)

            for offer in base_offers:
                report_line = price_report.get(offer.sku, {})

                extended_offer = YandexOfferInfo(
                    **asdict(offer),
                    attractive_price_threshold=report_line.get('attractive_price_threshold', 0),
                    moderately_attractive_price_threshold=report_line.get('moderately_attractive_price_threshold', 0),
                    best_place_wm=report_line.get('best_place_wm', ''),
                    best_price_wm=report_line.get('best_price_wm', 0),
                    best_place_im=report_line.get('best_place_im', ''),
                    best_price_im=report_line.get('best_price_im', 0),
                    minimum_group_price=report_line.get('minimum_group_price', 0),
                    your_price_for_buyers=report_line.get('your_price_for_buyers', 0),
                    group_sellers_amount=0,
                    remaining_stock=stocks.get(offer.sku, 0),
                    name_of_shop=campaign.business.name,
                )
                result.append(extended_offer)

        return result

    def check_response(self, response: Response, raise_error: bool = True, body: Any = None):
        if response.status_code != 200:
            if raise_error:
                self._raise_error(response.json(), response.status_code, body)
            else:
                print(response.reason, response.status_code, response.json(), body)

    def _raise_error(self, detail: str, status_code: int = 500, body: Any = None):
        # TODO write logs
        raise HTTPException(status_code, detail, body)

    def get_campaigns(self) -> [CampaignInfo]:
        response = self.session.get('https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)

        if response.status_code != 200:
            return None

        data = response.json()
        return [
            CampaignInfo(
                id=campaign['id'],
                client_id=campaign['clientId'],
                domain=campaign['domain'],
                business=BusinessInfo(
                    id=campaign['business']['id'],
                    name=campaign['business']['name']
                )

            )
            for campaign in data['campaigns']
        ]

    def get_stocks(self, campaign_id: int, handler: StocksResponseHandler = OFFERS) -> defaultdict[str, Any]:
        warehouses = []
        page_token = ''
        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/stocks?page_token={page_token}',
                headers=self.auth_headers
            )
            self.check_response(response)
            data = response.json()
            warehouses.extend(data['result']['warehouses'])

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break

        result = handler(warehouses)
        return result

    def _get_campaign_offers(self, business_id: int) -> [YandexOfferInfoPartial]:
        results = []
        page_token = ''
        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings?limit=200&page_token={page_token}',
                headers=self.auth_headers
            )

            self.check_response(response)
            data = response.json()

            for offer in data['result']['offerMappings']:
                offer = offer['offer']
                offer_data = YandexOfferInfoPartial(
                    sku=offer['offerId'],
                    name=offer['name'],
                    yandex_weight=offer['weightDimensions']['weight'] if 'weightDimensions' in offer else None,
                    yandex_length=offer['weightDimensions']['length'] if 'weightDimensions' in offer else None,
                    yandex_width=offer['weightDimensions']['width'] if 'weightDimensions' in offer else None,
                    yandex_height=offer['weightDimensions']['height'] if 'weightDimensions' in offer else None,
                    yandex_volume=(offer['weightDimensions']['length'] * offer['weightDimensions']['width'] *
                                   offer['weightDimensions']['height']) / 1000 if 'weightDimensions' in offer else None,
                    photo=offer['pictures'][0] if len(offer['pictures']) > 0 else None,
                    current_price=offer['basicPrice']['value'] if 'basicPrice' in offer else None,
                    business_id=business_id
                )
                results.append(offer_data)

            page_token = data['result']['paging'].get('nextPageToken', None)

            if page_token is None:
                break

        return results

    def change_offers_price(self, offers: pd.DataFrame | list[dict]) -> None:
        if isinstance(offers, pd.DataFrame):
            offers = offers.to_dict('records')

        chunk_size = 500
        for business_id in set([i['business_id'] for i in offers]):

            _offers = list(filter(lambda x: x['business_id'] == business_id, offers))

            for i in range(0, len(_offers), chunk_size):
                data = [{
                    'offerId': offer['sku'],
                    'price': {
                        'value': round(offer['target_price'], 2),
                        'currencyId': "RUR"
                    }
                }
                    for offer in _offers[i:i + chunk_size] if
                    (offer['target_price'] is not None and not np.isnan(offer['target_price'])) and offer['auto_price_control']]
                body = {
                    'offers': data
                }

                if not body['offers']:
                    continue

                response = self.session.post(
                    f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-prices/updates',
                    headers=self.auth_headers,
                    json=body
                )
                self.check_response(response, body=body, raise_error=False)

    def _download_report(self, url_path: str) -> pd.DataFrame:
        output = BytesIO()
        response = self.session.get(url_path)
        output.write(response.content)
        return pd.read_excel(output, engine='openpyxl')

    async def _get_market_prices_report(self, business_id: int) -> dict[str, dict[str, Any]]:
        response = self.session.post('https://api.partner.market.yandex.ru/reports/prices/generate',
                                     json={'businessId': business_id}, headers=self.auth_headers)

        if response.status_code != 200:
            self._raise_error(response.reason, response.status_code)

        data = response.json()
        report_id = data['result']['reportId']

        while True:
            response = self.session.get(f'https://api.partner.market.yandex.ru/reports/info/{report_id}',
                                        headers=self.auth_headers)

            data = response.json()

            if data['result']['status'] == 'DONE':
                df = self._download_report(data['result']['file'])
                df.drop([0, 1, 2, 3], inplace=True)
                new_df = pd.DataFrame()
                new_df[['sku', 'attractive_price_threshold', 'moderately_attractive_price_threshold',
                        'your_price_for_buyers', 'minimum_group_price', 'best_place_wm', 'best_price_wm', 'best_place_im',
                        'best_price_im']] = df.iloc[:, [0, 6, 7, 8, 11, 12, 13, 14, 15]]
                new_df.replace({'–': np.nan}, inplace=True)
                new_df[['best_place_wm', 'best_place_im']] = new_df[['best_place_wm', 'best_place_im']].fillna('')

                result = new_df.to_dict('records')
                result = {
                    i['sku']: {
                        'attractive_price_threshold': i['attractive_price_threshold'],
                        'moderately_attractive_price_threshold': i['moderately_attractive_price_threshold'],
                        'minimum_group_price': i['minimum_group_price'],
                        'best_place_wm': i['best_place_wm'],
                        'best_price_wm': i['best_price_wm'],
                        'best_place_im': str(i['best_place_im']).replace(' • FBY', '').replace(' • FBS', ''),
                        'best_price_im': i['best_price_im'],
                        'your_price_for_buyers': i['your_price_for_buyers']
                    }
                    for i in result
                }
                return result

            elif data['result']['status'] == 'FAILED':
                self._raise_error(response.reason, response.status_code)

            await asyncio.sleep(5)
