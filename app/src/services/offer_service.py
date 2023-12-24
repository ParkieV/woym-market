from src.api.repository import YandexMarketRepository
from src.params import confing as env
from src.database.db import async_session
from src.database import offer_db as db
import src.services.offer_utils as utils
from src.schemas.offer_schemas import OfferChange
import pandas as pd
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from ..database.models.models import Offer

yandex_repository = YandexMarketRepository(env.YANDEX_MARKET_TOKEN)


async def get_offers(limit: int = 600, offset: int = 0):
    async with async_session() as session:
        return await db.get_offers(session, limit, offset)


async def change_offer(offers_data: list[OfferChange]):
    async with async_session() as session:
        return await db.change_offer(session, offers_data)


async def setup_offers_data():
    yandex_offers = yandex_repository.get_offers()
    data = utils.build_offers_data(yandex_offers)

    async with async_session() as session:
        offers_db = await db.create_offers(session, data)
        return offers_db


async def update_offers():
    db_offers = jsonable_encoder(await get_offers())
    offers_df = pd.DataFrame(db_offers)
    yandex_offers = jsonable_encoder(yandex_repository.get_offers())
    yandex_offers_df = pd.DataFrame(yandex_offers)

    json_data = utils.update_offers_data(offers_df, yandex_offers_df)
    return json_data



async def build_csv():
    offers = jsonable_encoder(await get_offers())
    df = pd.DataFrame(offers)
    df.to_csv('data/out.csv', encoding='utf-8')
    return 'data/out.csv'
