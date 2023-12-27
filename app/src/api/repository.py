import json
from collections import defaultdict
from requests import Session, get
from src.schemas.yandex_api_schemas import ExtendedYandexOfferInfo, YandexOfferInfo, CampaignInfo
from asyncio import sleep
from fastapi import HTTPException
from io import BytesIO
import pandas as pd


class YandexMarketRepository:
    def __init__(self, token: str):
        self.session = Session()
        self.token = token
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }

    def raise_request_exception(self, status_code: int, detail: str):
        raise HTTPException(status_code, detail)

    async def get_offers(self) -> list[ExtendedYandexOfferInfo]:
        """Returns a list of full Yandex offers data"""
        campaigns = self.get_campaigns()

        offers_stock = {}
        for campaign in campaigns:
            offers_stock.update(self.get_offers_stocks(campaign.id))

        minimum_group_prices = {}
        for campaign in campaigns:
            minimum_group_prices.update(await self.get_market_price_report(campaign.id))

        offers: list[YandexOfferInfo] = []
        for campaign in campaigns:
            offers += self.get_campaign_offers(campaign.business_id)
            # path = await self.get_market_price_report(campaign.id)
            # print(path)
        print(len(offers))
        print(len(offers_stock.keys()))
        extended_offers = []
        for offer in offers:
            extended_offers.append(ExtendedYandexOfferInfo(
                **dict(offer),
                remaining_stock=offers_stock.get(offer.sku, 0),
                minimum_group_price=minimum_group_prices.get(offer.sku, 0),
                name_of_shop="",
                group_sellers_amount=0,
            ))
        return extended_offers

    def get_campaigns(self) -> list[CampaignInfo] | None:
        response = self.session.get('https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)

        if response.status_code != 200:
            return None

        data = response.json()
        return [
            CampaignInfo(
                id=campaign['id'],
                business_id=campaign['business']['id'],
                business_name=campaign['business']['name']
            )
            for campaign in data['campaigns']
        ]

    def get_offers_stocks(self, campaign_id: int) -> defaultdict[str, int] | None:
        stocks = defaultdict(int)
        page_token = ''
        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/stocks?page_token={page_token}&limit=200',
                headers=self.auth_headers
            )

            if response.status_code != 200:
                self.raise_request_exception(response.status_code, response.text)

            data = response.json()

            for warehouse in data['result']['warehouses']:
                for offer in warehouse['offers']:
                    stocks[offer['offerId']] += sum([i['count'] for i in offer['stocks'] if i['type'] == 'AVAILABLE'])

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break

        return stocks

    def get_campaign_offers(self, business_id: int) -> list[YandexOfferInfo] | None:
        results = []
        page_token = ''
        while True:
            response = self.session.post(
                f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings?limit=200&page_token={page_token}',
                headers=self.auth_headers
            )

            if response.status_code != 200:
                self.raise_request_exception(response.status_code, response.text)

            data = response.json()

            for offer in data['result']['offerMappings']:
                offer = offer['offer']
                if 'basicPrice' not in offer:
                    print(offer['offerId'], business_id)
                offer_data = YandexOfferInfo(
                    sku=offer['offerId'],
                    name=offer['name'],
                    weight=offer['weightDimensions']['weight'] if 'weightDimensions' in offer else 0,
                    length=offer['weightDimensions']['length'] / 100 if 'weightDimensions' in offer else 0,
                    width=offer['weightDimensions']['width'] / 100 if 'weightDimensions' in offer else 0,
                    height=offer['weightDimensions']['height'] / 100 if 'weightDimensions' in offer else 0,
                    volume_from_yandex=(offer['weightDimensions']['length'] * offer['weightDimensions']['width'] *
                                        offer['weightDimensions']['height']) / 5000 if 'weightDimensions' in offer else 0,
                    photo=offer['pictures'][0] if len(offer['pictures']) > 0 else None,
                    market_price=offer['basicPrice']['value'] if 'basicPrice' in offer else 0
                )
                results.append(offer_data)

            page_token = data['result']['paging'].get('nextPageToken', None)
            if page_token is None:
                break
        return results

    def update_offers_price(self, business_id: int, offers: dict):
        raise NotImplementedError()

        response = self.session.post(
            f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-prices/updates',
            headers=self.auth_headers,
            json=...
        )

        if response.status_code != 200:
            self.raise_request_exception(response.status_code, response.text)

    async def get_report_info(self, report_id: str):
        while True:
            response = self.session.get(f'https://api.partner.market.yandex.ru/reports/info/{report_id}',
                                        headers=self.auth_headers)

            data = response.json()

            if data['result']['status'] == 'DONE':
                path = self._download_report(data['result']['file'])
                return path
            elif data['result']['status'] == 'FAILED':
                self.raise_request_exception(response.status_code, response.text)

            await sleep(10)

    async def get_market_price_report(self, campaign_id: int):
        response = self.session.post('https://api.partner.market.yandex.ru/reports/prices/generate',
                                     json={'campaignId': campaign_id}, headers=self.auth_headers)

        if response.status_code != 200:
            self.raise_request_exception(response.status_code, response.text)

        data = response.json()
        report_id = data['result']['reportId']

        data = await self.get_report_info(report_id)
        return data

    def _download_report(self, url_path: str) -> dict[str, float]:
        output = BytesIO()
        response = self.session.get(url_path)
        output.write(response.content)
        df = pd.read_excel(output, engine='openpyxl')
        df.drop([0, 1, 2, 3], inplace=True)
        data: pd.DataFrame = df.iloc[:, [0, 10]].replace('–', 0)
        data.columns.values[0] = 'sku'
        data.columns.values[1] = 'price'

        d = dict()

        for i in json.loads(data.to_json(orient='records')):
            d[i['sku']] = i['price']

        return d
