import pytest
from collections import Counter
from src.api.yandex_market.api import YandexMarketAPI
from src.services.stocks_response_handlers import WAREHOUSES, OFFERS, OFFERS_DETAIL

api = YandexMarketAPI('y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU')
campaigns = api.get_campaigns()

pytest_plugins = ('pytest_asyncio',)


def test_stocks():
    assert len(campaigns) != 0

    for campaign in campaigns:
        stocks1 = api.get_stocks(campaign.id, WAREHOUSES)
        assert bool(len(stocks1))

        stocks2 = api.get_stocks(campaign.id, OFFERS)
        assert bool(len(stocks2))

        stock3 = api.get_stocks(campaign.id, OFFERS_DETAIL)
        assert len(stock3)
#
#
# def test_get_campaign_offers():
#     for campaign in campaigns:
#         offers = api._get_campaign_offers(campaign.business.id)
#
#         assert bool(len(offers))
#         assert len(offers) == len(set([i.sku for i in offers]))
#
#
# @pytest.mark.asyncio
# async def test_market_price_report():
#     for campaign in campaigns:
#         df = await api._get_market_prices_report(campaign.business.id)
#         assert df is not None


# @pytest.mark.asyncio
# async def test_get_offers():
#     offers = await api.get_offers()
#
#     assert len(offers)




