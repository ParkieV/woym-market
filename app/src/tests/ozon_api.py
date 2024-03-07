import pytest
from src.api.ozon.api import OzonAPI

api = OzonAPI(token='a66f89c1-73ef-487b-a051-f39875312fa2', entity_id=532844, shop_name='SkrabPlus')


pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_get_offers_identifiers():
    # ident = api._get_offers_identifiers()

    # assert ident

    # offers_info = api._get_offers_base_info(ident)
    # assert offers_info

    # offers_attributes = api._get_offers_attributes(ident)
    # assert offers_attributes

    # offers = await api.get_offers_list()
    # assert offers

    stocks = api._get_stock_on_warehouses()
    assert stocks

    data = await api.get_stocks()
    assert data


