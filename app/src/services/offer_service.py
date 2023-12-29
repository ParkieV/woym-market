from src.api.repository import YandexMarketRepository
from src.params import confing as env
from src.database.db import async_session
from src.database import offer_db as db
import src.services.offer_utils as utils
from src.schemas.offer_schemas import OfferChange, OfferOut, OfferDelete
import pandas as pd
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from src.services.user_service import get_settings
from ..database.models.models import Offer
import json


yandex_repository = YandexMarketRepository(env.YANDEX_MARKET_TOKEN)


async def get_offers():
    async with async_session() as session:
        return await db.get_offers(session)


async def change_offers(offers_data: list[OfferChange], user_id: int):
    settings = await get_settings(user_id)

    async with async_session() as session:
        offers = await db.get_offers_by_sku(session, [i.sku for i in offers_data])
        offers_df = pd.DataFrame(jsonable_encoder(offers))
        changes = pd.DataFrame(jsonable_encoder(offers_data))

        changed_offers = utils.update_offers_data(offers_df, changes, settings.rate)
        await db.update_offers(session, changed_offers)
        return await db.get_offers_by_sku(session, [i.sku for i in offers_data])
    # async with async_session() as session:
    #     return await db.change_offer(session, offers_data)


async def setup_offers_data(course: float = 15):
    yandex_offers = await yandex_repository.get_offers()
    yandex_offers_df = pd.DataFrame(jsonable_encoder(yandex_offers))
    data = utils.build_offers_data(yandex_offers_df, setup_mode=True, course=course)

    async with async_session() as session:
        offers_db = await db.create_offers(session, data)
        return offers_db


async def update_offers(user_id: int):
    settings = await get_settings(user_id)

    db_offers = jsonable_encoder(await get_offers())
    yandex_offers = jsonable_encoder(await yandex_repository.get_offers())

    offers_df = pd.DataFrame(db_offers)
    yandex_offers_df = pd.DataFrame(yandex_offers)

    db_offers_skus = set(offers_df['sku'])
    yandex_offers_skus = set(yandex_offers_df['sku'])

    print(db_offers_skus)
    print(yandex_offers_skus)

    to_delete_skus = db_offers_skus - yandex_offers_skus
    offers_df = offers_df[~offers_df['sku'].isin(to_delete_skus)]

    to_create_skus = yandex_offers_skus - db_offers_skus
    temp1 = yandex_offers_df[yandex_offers_df['sku'].isin(to_create_skus)]
    temp = utils.build_offers_data(temp1, settings.rate, setup_mode=True)
    to_create_rows = pd.DataFrame(temp)
    offers_df = pd.concat([offers_df, to_create_rows], ignore_index=True)

    json_data = utils.update_offers_data(offers_df, yandex_offers_df, settings.rate)

    async with async_session() as session:
        await db.delete_offers(session, to_delete_skus)
        await db.create_offers(session, json.loads(to_create_rows.to_json(orient='records')))
        await db.update_offers(session, json_data)
    return json_data


async def delete_offers(offers: list[OfferDelete]):
    async with async_session() as session:
        return await db.delete_offers(session, [i.sku for i in offers])


async def update_yandex_offers_price():
    async with async_session() as session:
        offers_db = jsonable_encoder(await db.get_offers(session))
        yandex_repository.update_offers_price(offers_db)


async def build_csv():
    offers = jsonable_encoder(await get_offers())
    df = pd.DataFrame(offers)
    df = df[OfferOut.__fields__.keys()]

    df.drop(['business_id'], axis=1, inplace=True)

    translated_columns = ['sku', 'Название', 'Вес', 'Длинна', 'Ширина', 'Высота', 'Объём с яндекса', 'Фото', 'Остатки на складах', 'Минимальная цена на рынке', 'Название магазина', 'Количество продавцов в группе', 'Закупка', 'Коэфициент расчетной цены', 'Объём', 'Себестоимость', 'Мин. наценка на расчетную цену', 'Расчетная цена', 'Цена до скидки', 'Прибыль', 'Окупаемость', 'Цена за FBY', 'Цена на маркете', 'Примечание 1', 'Примечание 2', 'Примечание 3', 'Автоматическое управление ценами', 'Ручное управление min цена']
    df.columns = translated_columns
    df.to_excel('data/out.xlsx', index=False)
    return 'data/out.xlsx'


async def import_offers_data(data: bytes, user_id: int):
    async with async_session() as session:
        settings = await get_settings(user_id)
        changes = utils.bytes_to_data_frame(data)
        changes.columns = list(OfferOut.__fields__.keys())

        db_offers = jsonable_encoder(await get_offers())
        offers_df = pd.DataFrame(db_offers)

        json_data = utils.update_offers_data(offers_df, changes, settings.rate)

        await db.update_offers(session, json_data)



