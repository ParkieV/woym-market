import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.schemas.offer_schemas import OfferOut
from .models.models import Offer
from typing import Iterable, Any


async def get_offers(session: AsyncSession, filters: dict[str, Any] | None = None) -> list[OfferOut]:
    query = select(Offer)

    if filters:
        query = query.filter_by(**filters)

    offers = await session.execute(query)
    return [OfferOut.model_validate(offer, from_attributes=True) for offer in offers.unique().scalars().all()]


async def create_offers(session: AsyncSession, data: list[dict] | pd.DataFrame) -> None:
    if isinstance(data, pd.DataFrame):
        data = data.to_dict('records')

    offers_db = [Offer(**offer_data) for offer_data in data]
    session.add_all(offers_db)
    await session.commit()


async def delete_offers(session: AsyncSession, offers_sku: Iterable[str]) -> None:
    query = delete(Offer).where(Offer.sku.in_(offers_sku))
    await session.execute(query)
    await session.commit()


async def update_offers(
        session: AsyncSession,
        data: list[dict] | pd.DataFrame,
        mapping_columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        endswith_sku: bool = False
) -> None:
    if isinstance(data, pd.DataFrame):
        data = data.to_dict('records')

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


async def get_offers_by_sku(session: AsyncSession, skus: list[str]) -> list[OfferOut]:
    query = select(Offer).where(Offer.sku.in_(skus))
    offers_db = await session.execute(query)
    return [OfferOut.model_validate(offer, from_attributes=True) for offer in offers_db.unique().scalars().all()]


async def get_offers_by_sku_and_shop_name(session: AsyncSession, data: list[tuple[str, str]]):
    result = []
    for offer in data:
        query = select(Offer).where((Offer.sku == offer[0]) & (Offer.name_of_shop == offer[1]))
        offers_db = await session.execute(query)
        result.append(offers_db.unique().scalars().one())

    return [OfferOut.model_validate(offer, from_attributes=True) for offer in result]
