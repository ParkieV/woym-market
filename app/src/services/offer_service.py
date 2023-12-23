from src.api.repository import YandexMarketRepository
from src.params import confing as env
from src.database.db import async_session
from src.database import offer_db as db
from .offer_utils import build_offers_data

yandex_repository = YandexMarketRepository(env.YANDEX_MARKET_TOKEN)


async def get_offers(limit: int = 600, offset: int = 0):
    async with async_session() as session:
        return await db.get_offers(session, limit, offset)


async def setup_offers_data():
    yandex_offers = yandex_repository.get_offers()
    data = build_offers_data(yandex_offers)

    async with async_session() as session:
        offers_db = await db.create_offers(session, data)
        return offers_db

