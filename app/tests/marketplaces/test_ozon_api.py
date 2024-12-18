import pytest
from datetime import datetime, timedelta
from src.api.ozon.api import OzonAPI
from src.schemas.base_api_schemas import APIOfferChangeData
from tests.marketplaces.conftest import BaseMarketplaceAPITest
from src.params.config import config
import pandas as pd  #noqa


@pytest.mark.parametrize(
    'api_class,auth_data',
    [(OzonAPI, {
        'token': 'a66f89c1-73ef-487b-a051-f39875312fa2',
        'entity_id': 532844,
        'shop_name': 'Skarb'
    })]
)
@pytest.mark.usefixtures('api')
class TestOzonAPI:

    async def test_get_offers_attributes(self, api: OzonAPI):
        idents = api._get_offers_identifiers()
        attributes = api._get_offers_attributes(idents)
        assert isinstance(attributes, dict)

    # async def test_set_search_words(self, api: OzonAPI):
    #     await api._set_search_words([('28165', 'секатор; сучкорез')])

    async def test_get_clasters_info(self, api: OzonAPI):
        clasters = api._get_clasters_info()
        assert isinstance(clasters, list)
        assert len(clasters)

    async def test_get_orders(self, api: OzonAPI):
        end = datetime.now(tz=config.time_zone_ino)
        start = end - timedelta(days=120)
        orders = await api.get_orders(start, end)

        assert isinstance(orders, list)
        assert orders

    async def test_change_offers(self, api: OzonAPI):
        data = [
            APIOfferChangeData(
                sku='28324',
                market='ozon',
                name_of_shop='Skrab',
                name='Катушка-головка для триммера \"ПАУК\" с леской М10 Al Skrab 28324',
                description='Катушка-головка для триммера \"ПАУК\" с леской М10 Al Skrab 28324 - это высококачественный инструмент, который станет незаменимым помощником в уходе за вашим садом.<br/><br/>Прочный и долговечный материал: ударопрочный монолитный алюминиевый корпус катушки-головки не имеет резьбы, что обеспечивает высокую прочность и долговечность изделия.<br/><br/>Легкая установка: катушка-головка устанавливается на триммер с помощью гайки от триммера, как и диски. В комплекте идут переходные шайбы под разные посадочные шпиндели.<br/><br/>Оптимальная длина лески: длина лески составляет 0,3 метра, а диаметр - 3,0 мм, что обеспечивает оптимальное сочетание прочности и гибкости для эффективной работы.<br/><br/>В комплекте шпулька: катушка-головка для триммера \"ПАУК\" с леской М10 Al Skrab 28324 поставляется с шпулькой, что позволяет быстро и легко менять леску без необходимости использования дополнительных инструментов.<br/><br/>Подходит для всех видов триммеров: данная катушка-головка подходит для всех видов триммеров, что делает ее отличным выбором для любого садовода.<br/><br/>Выбирая катушку-головку для триммера \"ПАУК\" с леской М10 Al Skrab 28324, вы получаете надежный и качественный инструмент, который облегчит уход за вашим садом и обеспечит эффективную работу на протяжении долгого времени.',
                search_words='нож строительный',
                self_weight='10',
                self_length='20',
                self_width='10',
                self_height='5',
            )
        ]
        # await api.change_offers(data)

    async def test_get_offers_list(self, api: OzonAPI):
        offers = await api.get_offers_list()
        assert isinstance(offers, list)
        assert offers
