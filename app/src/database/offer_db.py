from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from .models.models import Offer
from ..schemas.offer_schemas import OfferChange
import json
from typing import Iterable


async def get_offers(session: AsyncSession) -> list[Offer]:
    query = select(Offer)
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


async def change_offer(session: AsyncSession, offers_data: list[OfferChange]):
    for offer_data in offers_data:
        await session.execute(update(Offer).where(Offer.sku == offer_data.sku).values(**dict(offer_data)))

    await session.commit()
    return None


async def update_offers(session: AsyncSession, offers_data):
    for offer_data in offers_data:
        del offer_data['id']
        await session.execute(update(Offer).where(Offer.sku == offer_data['sku']).values(**offer_data))

    await session.commit()
    return None


async def get_offers_by_sku(session: AsyncSession, skus: list[str]):
    query = select(Offer).where(Offer.sku.in_(skus))
    offers_db = await session.execute(query)
    return offers_db.unique().scalars().all()

