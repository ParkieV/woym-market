import pytest

from src.api.factory import APIFactory, APITypes


api1 = APIFactory.get(APITypes.YANDEX, token='y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU', entity_id=21952451, shop_name='CALMAR.SHOP')
api2 = APIFactory.get(APITypes.YANDEX, token='y0_AgAAAAAW8Hr_AAsIRgAAAAD1j7NA7uQ9YJbpR-elaniG1o-TiKxVJhU', entity_id=82457010, shop_name='MASTERSKRAB')

pytest_plugins = ('pytest_asyncio',)


# @pytest.mark.asyncio
# async def test_get_warehouses_info():
#     warehouses1 = await api1.get_stocks()
#     assert len(warehouses1)
#
#     warehouses2 = await api2.get_stocks()
#     assert len(warehouses2)


@pytest.mark.asyncio
async def test_get_offers():
    offers1 = await api1.get_offers_list()
    assert len(offers1)

    offers2 = await api2.get_offers_list()
    assert len(offers2)






