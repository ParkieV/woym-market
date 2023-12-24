from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models.models import Offer
from ..schemas.offer_schemas import OfferChange


async def get_offers(session: AsyncSession, limit: int = 600, offset: int = 0) -> list[Offer]:
    query = select(Offer).offset(offset).limit(limit)
    offers = await session.execute(query)
    return offers.unique().scalars().all()


async def create_offers(session: AsyncSession, offers_data):
    offers_db = [Offer(**offer_data) for offer_data in offers_data]

    for offer_db in offers_db:
        session.add(offer_db)

    await session.commit()
    return None


async def change_offer(session: AsyncSession, offers_data: list[OfferChange]):
    for offer_data in offers_data:
        await session.execute(update(Offer).where(Offer.sku == offer_data.sku).values(**offer_data.model_dump()))

    await session.commit()
    return None



