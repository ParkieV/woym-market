from src.api.yandex_market.api import YandexMarketAPI
from src.api.repositories import BaseRepository


class YandexMarketRepository(BaseRepository):
    def __init__(self, api: YandexMarketAPI):
        self._api = api

    async def get_offers(self):
        ...

    async def get_stocks(self):
        ...

    def change_prices(self):
        ...


# class YandexMarketWebParser:
#     HEADERS = {
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#         'Connection': 'keep-alive',
#         'Host': 'market.yandex.ru',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'none',
#         'Sec-Fetch-User': '?1',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
#         }
#
#     async def get_offer(self, url: str):
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url, headers=self.HEADERS) as response:
#                 text = await response.read()
#                 data = BeautifulSoup(text)
#                 print(data)
#                 print(data.find('h3', _class='_1stjo'))
#                 print(data.find('span', _class='_8-sD9'))


# class YandexMarketRepository:
#     def __init__(self, token: str):
#         self.session = Session()
#         self.token = token
#         self.auth_headers = {
#             'Authorization': f'Bearer {token}'
#         }
#
#     def raise_request_exception(self, status_code: int, detail: str):
#         raise HTTPException(status_code, detail)
#
#     async def get_offers(self) -> list[ExtendedYandexOfferInfo]:
#         """Returns a list of full Yandex offers data"""
#         campaigns = self.get_campaigns()
#
#         offers_stock = {}
#         for campaign in campaigns:
#             offers_stock.update(self.get_offers_stocks(campaign.id))
#
#         minimum_group_prices = {}
#         for campaign in campaigns:
#             minimum_group_prices.update(await self.get_market_price_report(campaign.business_id))
#
#         offers: list[YandexOfferInfo] = []
#         for campaign in campaigns:
#             offers += self.get_campaign_offers(campaign.business_id)
#
#         extended_offers = []
#         for offer in offers:
#             extended_offers.append(ExtendedYandexOfferInfo(
#                 **dict(offer),
#                 remaining_stock=offers_stock.get(offer.sku, 0),
#                 minimum_group_price=minimum_group_prices[offer.sku][
#                     'price'] if offer.sku in minimum_group_prices.keys() else 0,
#                 minimum_group_price_shop=minimum_group_prices[offer.sku][
#                     'shop'] if offer.sku in minimum_group_prices.keys() else None,
#                 name_of_shop=list(filter(lambda x: x.business_id == offer.business_id, campaigns))[0].business_name,
#                 group_sellers_amount=0,
#             ))
#         return extended_offers
#
#     def get_campaigns(self) -> list[CampaignInfo] | None:
#         return [CampaignInfo(id=21952451, business_id=980790, business_name="CALMAR.SHOP")]
#
#         # TODO баги с остатками на складах при использовании с несколькими компаниями
#         response = self.session.get('https://api.partner.market.yandex.ru/campaigns', headers=self.auth_headers)
#
#         if response.status_code != 200:
#             return None
#
#         data = response.json()
#         return [
#             CampaignInfo(
#                 id=campaign['id'],
#                 business_id=campaign['business']['id'],
#                 business_name=campaign['business']['name']
#             )
#             for campaign in data['campaigns']
#         ]
#
#     def get_offers_stocks(self, campaign_id: int) -> defaultdict[str, int] | None:
#         stocks = defaultdict(int)
#         page_token = ''
#         while True:
#             response = self.session.post(
#                 f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/stocks?page_token={page_token}&limit=200',
#                 headers=self.auth_headers
#             )
#
#             if response.status_code != 200:
#                 self.raise_request_exception(response.status_code, response.text)
#
#             data = response.json()
#
#             for warehouse in data['result']['warehouses']:
#                 for offer in warehouse['offers']:
#                     stocks[offer['offerId']] += sum([i['count'] for i in offer['stocks'] if i['type'] == 'AVAILABLE'])
#
#             page_token = data['result']['paging'].get('nextPageToken', None)
#             if page_token is None:
#                 break
#
#         return stocks
#
#     def get_campaign_offers(self, business_id: int) -> list[YandexOfferInfo] | None:
#         results = []
#         page_token = ''
#         while True:
#             response = self.session.post(
#                 f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings?limit=200&page_token={page_token}',
#                 headers=self.auth_headers
#             )
#
#             if response.status_code != 200:
#                 self.raise_request_exception(response.status_code, response.text)
#
#             data = response.json()
#
#             for offer in data['result']['offerMappings']:
#                 offer = offer['offer']
#                 offer_data = YandexOfferInfo(
#                     sku=offer['offerId'],
#                     name=offer['name'],
#                     weight=offer['weightDimensions']['weight'] if 'weightDimensions' in offer else 0,
#                     length=offer['weightDimensions']['length'] if 'weightDimensions' in offer else 0,
#                     width=offer['weightDimensions']['width'] if 'weightDimensions' in offer else 0,
#                     height=offer['weightDimensions']['height'] if 'weightDimensions' in offer else 0,
#                     volume_yandex=(offer['weightDimensions']['length'] * offer['weightDimensions']['width'] *
#                                    offer['weightDimensions']['height']) / 5000 if 'weightDimensions' in offer else 0,
#                     photo=offer['pictures'][0] if len(offer['pictures']) > 0 else None,
#                     current_price=offer['basicPrice']['value'] if 'basicPrice' in offer else None,
#                     business_id=business_id
#                 )
#                 results.append(offer_data)
#
#             page_token = data['result']['paging'].get('nextPageToken', None)
#             if page_token is None:
#                 break
#         return results
#
#     def update_offers_price(self, offers: list[dict]):
#         chunk_size = 500
#         for business_id in set([i['business_id'] for i in offers]):
#             _offers = list(filter(lambda x: x['business_id'] == business_id, offers))
#             for i in range(0, len(_offers), chunk_size):
#                 data = [{
#                     'offerId': offer['sku'],
#                     'price': {
#                         'value': offer['target_price'],
#                         'currencyId': "RUR"
#                     }
#                 }
#                     for offer in _offers[i:i + chunk_size] if
#                     offer['target_price'] is not None and offer['auto_price_control']]
#                 body = {
#                     'offers': data
#                 }
#
#                 if len(body['offers']) <= 0:
#                     continue
#
#                 response = self.session.post(
#                     f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-prices/updates',
#                     headers=self.auth_headers,
#                     json=body
#                 )
#
#                 if response.status_code != 200:
#                     self.raise_request_exception(response.status_code, response.text)
#
#     async def get_report_info(self, report_id: str):
#         while True:
#             response = self.session.get(f'https://api.partner.market.yandex.ru/reports/info/{report_id}',
#                                         headers=self.auth_headers)
#
#             data = response.json()
#
#             if data['result']['status'] == 'DONE':
#                 path = self._download_report(data['result']['file'])
#                 return path
#             elif data['result']['status'] == 'FAILED':
#                 self.raise_request_exception(response.status_code, response.text)
#
#             await sleep(10)
#
#     async def get_market_price_report(self, business_id: int):
#         response = self.session.post('https://api.partner.market.yandex.ru/reports/prices/generate',
#                                      json={'businessId': business_id}, headers=self.auth_headers)
#
#         if response.status_code != 200:
#             self.raise_request_exception(response.status_code, response.text)
#
#         data = response.json()
#         report_id = data['result']['reportId']
#
#         data = await self.get_report_info(report_id)
#         return data
#
#     def _download_report(self, url_path: str) -> dict[str, tuple[float, str]]:
#         output = BytesIO()
#         response = self.session.get(url_path)
#         output.write(response.content)
#         df = pd.read_excel(output, engine='openpyxl')
#         df.drop([0, 1, 2, 3], inplace=True)
#         new_df = pd.DataFrame()
#         new_df[['sku', 'shop', 'price']] = df.iloc[:, [0, 13, 14]].replace('–', 0)
#
#         result = new_df.to_dict('records')
#         result = {i['sku']: {'price': i['price'], 'shop': str(i['shop']).replace(' • FBY', '').replace(' • FBS', '')}
#                   for i in result}
#
#         return result


# if __name__ == '__main__':
#     parser = YandexMarketWebParser()
#     loop = asyncio.get_event_loop()
#     # https://market.yandex.ru/product--stroitelnyi-ugolnik-skrab-40306/1778025404/offers?how=aprice&lr=213&sku=573232051&cpa=1&grhow=supplier&local-offers-first=0
#     loop.run_until_complete(parser.get_offer(
#         'https://market.yandex.ru/product--stroitelnyi-ugolnik-skrab-40306/1778025404/offers?lr=213&sku=573232051&how=aprice&_redirectCount=1'))
