from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models.models import Offer


async def get_offers(session: AsyncSession, limit: int = 600, offset: int = 0) -> list[Offer]:
    query = select(Offer).offset(offset).limit(limit)
    offers = await session.execute(query)
    return offers.scalars()


async def create_offers(session: AsyncSession, offers_data):
    offers_db = [Offer(**offer_data) for offer_data in offers_data]

    for offer_db in offers_db:
        session.add(offer_db)

    await session.commit()
    return None

