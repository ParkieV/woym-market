from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from .models.models import Offer
from ..schemas.offer_schemas import OfferChange
import json
from typing import Iterable, Any


async def get_offers(session: AsyncSession, filters: dict[str, Any] | None = None) -> list[Offer]:
    query = select(Offer)

    if filters:
        query = query.filter_by(**filters)

    offers = await session.execute(query)
    return offers.unique().scalars().all()


async def create_offers(session: AsyncSession, offers_data):
    offers_db = [Offer(**offer_data) for offer_data in offers_data]

    for offer_db in offers_db:
        session.add(offer_db)

    await session.commit()
    return None


async def delete_offers(session: AsyncSession, offers_sku: Iterable[str]):
    query = delete(Offer).where(Offer.sku.in_(offers_sku))
    await session.execute(query)
    await session.commit()
    return None


# async def update_offers(session: AsyncSession, offers_data, find_with_shop_name: bool = True, endswith_sku: bool = False):
#     for offer_data in offers_data:
#         if 'id' in offer_data.keys():
#             del offer_data['id']
#
#         if endswith_sku:
#             sku_query = Offer.sku.endswith(offer_data['sku'])
#         else:
#             sku_query = Offer.sku == offer_data['sku']
#
#         del offer_data['sku']
#
#         if find_with_shop_name:
#             await session.execute(update(Offer).where(sku_query & (Offer.name_of_shop == offer_data['name_of_shop'])).values(**offer_data))
#         else:
#             await session.execute(update(Offer).where(sku_query).values(**offer_data))
#
#     await session.commit()

async def update_offers(
        session: AsyncSession,
        data: list[dict],
        mapping_columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        endswith_sku: bool = False
):
    for offer in data:
        if 'id' in offer.keys():
            del offer['id']

        query = update(Offer)

        if filters:
            query = query.filter_by(**filters)

        if mapping_columns:
            query = query.filter_by(**{column: offer[column] for column in mapping_columns})

        if endswith_sku:
            query = query.where(Offer.sku.endswith(offer['sku']))
            del offer['sku']
        else:
            query = query.where(Offer.sku == offer['sku'])

        await session.execute(query.values(**offer))

    await session.commit()


async def get_offers_by_sku(session: AsyncSession, skus: list[str]):
    query = select(Offer).where(Offer.sku.in_(skus))
    offers_db = await session.execute(query)
    return offers_db.unique().scalars().all()


async def get_offers_by_sku_and_shop_name(session: AsyncSession, data: list[tuple[str, str]]):
    result = []
    for offer in data:
        query = select(Offer).where((Offer.sku == offer[0]) & (Offer.name_of_shop == offer[1]))
        offers_db = await session.execute(query)
        result.append(offers_db.unique().scalars().one())

    return result
