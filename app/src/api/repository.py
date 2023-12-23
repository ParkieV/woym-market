from collections import defaultdict
from requests import Session
from src.schemas.yandex_api_schemas import ExtendedYandexOfferInfo, YandexOfferInfo, CampaignInfo


class YandexMarketRepository:
    def __init__(self, token: str):
        self.session = Session()
        self.token = token
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }

    def get_offers(self) -> list[ExtendedYandexOfferInfo]:
        campaigns = self.get_campaigns()

        offers_stock = {}
        for campaign in campaigns:
            offers_stock.update(self.get_offers_stocks(campaign.id))

        offers: list[YandexOfferInfo] = []
        for campaign in campaigns:
            offers += self.get_campaign_offers(campaign.business_id)

        extended_offers = []
        for offer in offers:
            extended_offers.append(ExtendedYandexOfferInfo(
                **offer.model_dump(),
                remaining_stock=offers_stock[offer.sku],
                minimum_group_price=0,
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
        response = self.session.post(
            f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/stocks',
            headers=self.auth_headers
        )

        if response.status_code != 200:
            return None

        data = response.json()
        stocks = defaultdict(int)

        for warehouse in data['result']['warehouses']:
            for offer in warehouse['offers']:
                stocks[offer['offerId']] += sum([i['count'] for i in offer['stocks'] if i['type'] == 'AVAILABLE'])

        return stocks

    def get_campaign_offers(self, business_id: int) -> list[YandexOfferInfo] | None:
        # implement offset and limit
        response = self.session.post(
            f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings',
            headers=self.auth_headers
        )

        if response.status_code != 200:
            return None

        data = response.json()
        results = []

        for offer in data['result']['offerMappings']:
            offer = offer['offer']
            results.append(YandexOfferInfo(
                sku=offer['offerId'],
                name=offer['name'],
                weight=offer['weightDimensions']['weight'],
                length=offer['weightDimensions']['length'],
                width=offer['weightDimensions']['width'],
                height=offer['weightDimensions']['height'],
                volume_from_yandex=0, # не нашел
                photo=offer['pictures'][0] if len(offer['pictures']) > 0 else None,
            ))

        return results

    def update_campaign_offers(self, campaign_id: int, offers: dict):
        raise NotImplementedError()

