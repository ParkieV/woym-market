import numpy as np
import pandas as pd
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.schemas.offer_schemas import OfferOut, PricingSchemeOut, PricingSchemeChange, PricingSchemeCreate, BaseOffer
from .models.models import Offer, PricingScheme
from typing import Iterable, Any, Type
from fastapi.exceptions import HTTPException
from fastapi import status


def _dataframe_to_valid_dict(data: pd.DataFrame | list[dict]):
    '''Converts data to a valid sqlalchemy entry. If data is not a DataFrame, returns data'''
    if not isinstance(data, pd.DataFrame):
        return data

    data = data.copy()
    data = data.replace(np.nan, None)
    data = data.to_dict('records')
    return data


async def get_offers(session: AsyncSession, filters: dict[str, Any] | None = None, model_schema: Type[BaseModel] = OfferOut) -> list[OfferOut]:
    query = select(Offer)

    if filters:
        query = query.filter_by(**filters)

    offers = await session.execute(query)
    return [model_schema.model_validate(offer, from_attributes=True) for offer in offers.unique().scalars().all()]


async def create_offers(session: AsyncSession, data: list[dict] | pd.DataFrame) -> None:
    data = _dataframe_to_valid_dict(data)

    offers_db = [Offer(**offer_data) for offer_data in data]
    session.add_all(offers_db)
    await session.commit()


async def delete_offers(session: AsyncSession, data: list[dict] | pd.DataFrame) -> None:
    data = _dataframe_to_valid_dict(data)

    for offer in data:
        query = delete(Offer).filter_by(**offer)
        await session.execute(query)

    await session.commit()


async def update_offers(
        session: AsyncSession,
        data: list[dict] | pd.DataFrame,
        mapping_columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        endswith_sku: bool = False,
) -> None:
    data = _dataframe_to_valid_dict(data)

    for offer in data:
        if 'id' in offer.keys():
            del offer['id']

        if 'manual_min_price' in offer.keys() and offer['manual_min_price'] is None:
            del offer['manual_min_price']

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


async def get_offers_by(session: AsyncSession, data: list[dict[str, Any]] | pd.DataFrame, model_schema: Type[BaseModel] = OfferOut):
    data = _dataframe_to_valid_dict(data)

    result = []
    for offer_data in data:
        query = select(Offer).filter_by(**offer_data)
        query_result = await session.execute(query)
        result.extend([model_schema.model_validate(offer, from_attributes=True) for offer in query_result.scalars().all()])

    return result


async def get_offer(session: AsyncSession, filters: dict, model_schema: Type[BaseOffer] = OfferOut):
    query = select(Offer).filter_by(**filters)
    result = await session.execute(query)
    return model_schema.model_validate(result.scalar_one(), from_attributes=True)


async def create_pricing_scheme(session: AsyncSession, data: PricingSchemeCreate | dict) -> PricingSchemeOut:
    if isinstance(data, PricingSchemeCreate):
        data = data.model_dump()

    scheme_db = PricingScheme(**data)
    session.add(scheme_db)
    await session.commit()
    await session.refresh(scheme_db)

    return PricingSchemeOut.model_validate(scheme_db, from_attributes=True)


async def delete_pricing_scheme(session: AsyncSession, data: list[int]):
    query = delete(PricingScheme).where(PricingScheme.id.in_(data))
    await session.execute(query)
    await session.commit()


async def get_pricing_schemes(session: AsyncSession) -> list[PricingSchemeOut]:
    query = select(PricingScheme)
    scheme_db = await session.execute(query)

    return [PricingSchemeOut.model_validate(scheme, from_attributes=True) for scheme in
            scheme_db.unique().scalars().all()]


async def change_pricing_scheme(session: AsyncSession, data: PricingSchemeChange | dict):
    if isinstance(data, PricingSchemeChange):
        data = data.model_dump()

    query = update(PricingScheme).where(PricingScheme.id == data['id']).values(**data)
    await session.execute(query)
    await session.commit()


async def validate_pricing_scheme_id(session: AsyncSession, data: int | Iterable[int]) -> None:
    if isinstance(data, int):
        data = [data]

    for i in data:
        query = select(PricingScheme).where(PricingScheme.id == i)
        rez = await session.execute(query)

        if rez.scalar_one_or_none() is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Схемы ценообразования с id - {i} не найдено')


async def get_unique_skus(session: AsyncSession) -> list[str]:
    query = select(Offer.sku).distinct()
    result = await session.execute(query)
    return [i[0] for i in result.all()]
