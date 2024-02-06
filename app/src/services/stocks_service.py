from src.database.db import async_session
from src.database import warehouse_db as db
from src.api.factory import APIFactory, MPTypes
from src.params.confing import config

yandex_api = APIFactory.get(MPTypes.YANDEX, token=config.yandex_token)


async def setup_warehouses_and_stocks():
    stocks = await yandex_api.get_stocks()

    async with async_session() as session:
        pass