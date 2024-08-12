from datetime import datetime

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from src.schemas.offer_schemas import OfferOut, PricingSchemeOut, PricingSchemeCreate, PricingSchemeFieldCreate, PricingSchemeFieldOut, PricingSchemeFieldChange, PricingSchemeChange, ViolatorDTO
from .models.models import Offer, PricingScheme, PricingSchemeField, \
    remaining_stocks_subuery
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


async def get_offers(session: AsyncSession, filters: dict[str, Any] | None = None, model_schema: Type[BaseModel] = OfferOut, offset: int = 0, limit: int | None = None) -> list[OfferOut]:
    query = select(
        Offer,
        remaining_stocks_subuery.c.remaining_stock
    ).outerjoin(remaining_stocks_subuery, remaining_stocks_subuery.c.offer_id == Offer.id)

    if filters:
        query = query.filter_by(**filters)

    query = query.offset(offset)
    if limit:
        query = query.limit(limit)

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


async def get_offers_by(session: AsyncSession, data: list[dict[str, Any]] | pd.DataFrame,
                        model_schema: Type[BaseModel] = OfferOut):
    data = _dataframe_to_valid_dict(data)

    result = []
    for offer_data in data:
        query = (
            select(
                Offer.columns(use_catalog=True),
                remaining_stocks_subuery.c.remaining_stock
            )
            .join(remaining_stocks_subuery, remaining_stocks_subuery.c.offer_id == Offer.id)
            .filter_by(**offer_data)
        )
        query_result = await session.execute(query)
        result.extend(
            [model_schema.model_validate(offer, from_attributes=True) for offer in query_result.scalars().all()])

    return result


async def validate_pricing_scheme_field_data(session: AsyncSession, data: PricingSchemeFieldCreate | dict):
    if isinstance(data, PricingSchemeFieldCreate):
        data = data.model_dump()

    if data['key'] not in OfferOut.fields().keys():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Поля '{data['key']}' нет в модели Offer")

    query = select(PricingScheme).where(PricingScheme.name == data['pricing_scheme_name']).options(
        selectinload(PricingScheme.fields))
    result = (await session.execute(query)).scalar_one_or_none()

    if result is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Схемы с именем {data["pricing_scheme_name"]} не найдено')

    target_scheme_field_keys = [i.key for i in result.fields]

    if data['key'] in target_scheme_field_keys:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Поле с ключем {data["key"]} уже есть в схеме {result.name}')

    return data


async def create_pricing_scheme_field(session: AsyncSession,
                                      data: PricingSchemeFieldCreate | dict) -> PricingSchemeFieldOut:
    if isinstance(data, PricingSchemeFieldCreate):
        data = data.model_dump()

    data = await validate_pricing_scheme_field_data(session, data)
    field_db = PricingSchemeField(**data)
    session.add(field_db)
    await session.commit()
    await session.refresh(field_db)
    return PricingSchemeFieldOut.model_validate(field_db, from_attributes=True)


async def change_pricing_scheme_field(session: AsyncSession, data: list[PricingSchemeFieldChange]):
    for field in data:
        stmp = update(PricingSchemeField).where(PricingSchemeField.id == field.id).values(**field.model_dump())
        await session.execute(stmp)
    await session.commit()


async def create_pricing_scheme(session: AsyncSession, data: PricingSchemeCreate) -> PricingSchemeOut:
    pricing_scheme_data = data.model_dump()
    fields_data = [i for i in pricing_scheme_data['fields']]
    del pricing_scheme_data['fields']

    pricing_scheme_db = PricingScheme(**pricing_scheme_data)
    session.add(pricing_scheme_db)
    await session.commit()
    await session.refresh(pricing_scheme_db)

    for field in fields_data:
        await create_pricing_scheme_field(session, PricingSchemeFieldCreate(**field))


async def change_pricing_scheme(session: AsyncSession, data: PricingSchemeChange):
    base_scheme = data.model_dump()
    del base_scheme['fields']
    stmp = update(PricingScheme).where(PricingScheme.name == data.name).values(**base_scheme)
    await session.execute(stmp)
    await session.commit()
    await change_pricing_scheme_field(session, data.fields)


async def delete_pricing_scheme(session: AsyncSession, names: list[str]):
    query = delete(PricingScheme).where(PricingScheme.name.in_(names))
    await session.execute(query)
    await session.commit()


async def get_pricing_schemes(session: AsyncSession) -> list[PricingSchemeOut]:
    query = select(PricingScheme).options(selectinload(PricingScheme.fields))
    scheme_db = await session.execute(query)

    return [PricingSchemeOut.model_validate(scheme, from_attributes=True) for scheme in
            scheme_db.unique().scalars().all()]


async def check_pricing_schemes_exists(session: AsyncSession, name: str):
    query = select(PricingScheme).where(PricingScheme.name == name)
    result = await session.execute(query)

    if not result.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Схемы ценообразования {name} не найдено')


async def delete_pricing_scheme_fields(session: AsyncSession, ids: list[int]):
    stmp = delete(PricingSchemeField).where(PricingSchemeField.id.in_(ids))
    await session.execute(stmp)
    await session.commit()


async def get_unique_skus(session: AsyncSession) -> list[str]:
    query = select(Offer.sku).distinct()
    result = await session.execute(query)
    return [i[0] for i in result.all()]


async def set_supplier_available(session: AsyncSession, skus: Iterable[str], value: bool) -> None:
    for sku in skus:
        stmp = update(Offer).where(Offer.sku.endswith(sku)).values(supplier_available=value)
        await session.execute(stmp)
        await session.commit()


async def set_dollar_cost_price_updated_at(session: AsyncSession, skus: Iterable[str], value: datetime) -> None:
    for sku in skus:
        stmp = update(Offer).where(Offer.sku.endswith(sku)).values(dollar_cost_price_updated_at=value)
        await session.execute(stmp)
        await session.commit()


async def get_violators(session: AsyncSession, market: str | None = None, name_of_shop: str | None = None) -> list[ViolatorDTO]:
    query = select(
        Offer.best_place_im.label('name_of_shop'),
        Offer.market,
        Offer.min_price_in_market.label('price'),
        Offer.recommended_retail_price,
        Offer.best_place_im_link.label('link')
    ).where(Offer.recommended_retail_price > Offer.min_price_in_market)

    if market:
        query = query.where(Offer.market == market)

    if name_of_shop:
        query = query.where(Offer.name_of_shop == name_of_shop)

    result = (await session.execute(query)).all()
    return [ViolatorDTO.model_validate(i, from_attributes=True) for i in result]
