from collections.abc import Hashable, AsyncGenerator
from datetime import datetime
from operator import or_

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from src.schemas.offer_schemas import OfferOut, PricingSchemeOut, PricingSchemeCreate, PricingSchemeFieldCreate, PricingSchemeFieldOut, PricingSchemeFieldChange, PricingSchemeChange, ViolatorDTO
from .models.models import Offer, PricingScheme, PricingSchemeField, \
    remaining_stocks_subuery
from typing import Iterable, Any, Type, TypeVar
from fastapi.exceptions import HTTPException
from fastapi import status

from ..schemas.filters.filter_schemas import PagingFilter
from ..schemas.filters.offers_filter import OffersFilter, OffersSourceFilter


def _dataframe_to_valid_dict(data: pd.DataFrame | list[dict]):
    '''Converts data to a valid sqlalchemy entry. If data is not a DataFrame, returns data'''
    if not isinstance(data, pd.DataFrame):
        return data

    data = data.copy()
    data = data.replace(np.nan, None)
    data = data.to_dict('records')
    return data


async def get_offers_list(session: AsyncSession,
                          *,
                          chunk_size: int | None = None,
                          offers_filter: OffersFilter | None = None) -> AsyncGenerator[list[OfferOut], None]:
    """
    Get offers from DB using chunks
    :param session: SQLAlchemy asynchronous session
    :param chunk_size: size of chunk
    :param offers_filter: filters for selecting offers
    :return: Batch of offers
    """
    query = select(Offer)

    if offers_filter:
        query = offers_filter(query)


    offset = 0
    while True:
        query = query.limit(chunk_size).offset(offset)
        offer_chunk = (await session.execute(query)).scalars().all()
        res = [OfferOut.model_validate(offer, from_attributes=True) for offer in offer_chunk]

        if len(res) == 0:
            return

        yield res
        offset += chunk_size


def clear_dict_from_keys(keys: list[Hashable], dictionary: dict[Hashable, Any]) -> dict[Hashable, Any]:
    for key in keys:
        try:
            dictionary.pop(key)
        except KeyError:
            pass
    return dictionary

async def create_offers(session: AsyncSession, data: list[dict] | pd.DataFrame) -> None:
    data = _dataframe_to_valid_dict(data)

    offers_db = [Offer(**clear_dict_from_keys(['yandex_volume', 'volume', 'volume_difference'],
                                              offer_data)) for offer_data in data]
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
        detect_changes: list[str] | None = None,
) -> None:
    data = _dataframe_to_valid_dict(data)

    for offer in data:
        if 'id' in offer.keys():
            del offer['id']

        # Поисковые слова изменяются только у озона
        if 'search_words' in offer and offer.get('market', None) != 'ozon':
            del offer['search_words']

        if 'barcodes' in offer and offer.get('market', None) != 'yandex':
            del offer['barcodes']

        stmp = update(Offer)

        if filters:
            stmp = stmp.filter_by(**filters)

        if mapping_columns:
            stmp = stmp.filter_by(**{column: offer[column] for column in mapping_columns})

        if endswith_sku:
            stmp = stmp.where(Offer.sku.endswith(offer['sku']))
            del offer['sku']
        else:
            stmp = stmp.where(Offer.sku == offer['sku'])

        if detect_changes:
            tracked_data = {f'{i}_changed': or_(getattr(Offer, f'{i}_changed'), (func.coalesce(getattr(Offer, i), 'unknown') != (offer[i] or 'unknown'))) for i in detect_changes if getattr(Offer, i, None) and i in offer}
            offer.update(tracked_data)

        offers_db = clear_dict_from_keys(['yandex_volume', 'volume', 'volume_difference'],
                                                  offer)

        stmp = stmp.values(**offers_db)

        await session.execute(stmp)

        await session.commit()

async def change_offers(
        session: AsyncSession,
        offers: list[dict],
        mapping_fields: list[str],
        detect_changes: list[str] | None = None,
        offers_filter: OffersSourceFilter | None = None,
) -> None:
    offer_model_update_fields = {i: getattr(Offer, i) for i in mapping_fields}

    for update_offer_data in offers:
        if (set(offer_model_update_fields.keys()) & set(update_offer_data.keys()) & set(mapping_fields)) != set(mapping_fields):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Поля {mapping_fields} обязательно должны быть переданы')

        if detect_changes:
            tracked_data = {
                f'{i}_changed': func.concat(getattr(Offer, i), '') != func.concat(update_offer_data[i], '')
                for i in detect_changes if getattr(Offer, i, None) and i in update_offer_data
            }
            update_offer_data.update(tracked_data)

        stmp = update(Offer).values(**update_offer_data)

        for mapping_field in mapping_fields:
            stmp = stmp.where(offer_model_update_fields[mapping_field] == update_offer_data[mapping_field])

        if offers_filter:
            stmp = offers_filter(stmp)

        await session.execute(stmp)

    await session.commit()


async def get_offers_by(session: AsyncSession, data: list[dict[str, Any]] | pd.DataFrame,
                        model_schema: Type[BaseModel] = OfferOut):
    data = _dataframe_to_valid_dict(data)

    result = []
    for offer_data in data:
        query = (
            select(
                Offer.__table__.columns,
                remaining_stocks_subuery.c.remaining_stock
            )
            .filter_by(**offer_data)
            .join(remaining_stocks_subuery, remaining_stocks_subuery.c.offer_id == Offer.id)

        )
        query_result = await session.execute(query)
        result.extend(
            [model_schema.model_validate(offer, from_attributes=True) for offer in query_result.all()])

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
        stmp = update(Offer).where(Offer.sku.endswith(sku)).values(
            supplier_available=value,
            dollar_cost_price_updated_at=func.now(),
        )
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


async def get_offers_fields(session: AsyncSession, columns: list):
    query = select(
        *columns
    )
    result = (await session.execute(query)).all()
    return result

async def reset_all_track_offers_markers(session: AsyncSession):
    stmp = update(Offer).values(
        name_changed=False,
        description_changed=False,
        self_weight_changed=False,
        self_length_changed=False,
        self_width_changed=False,
        self_height_changed=False,
        barcodes_changed=False,
        search_words_changed=False
    )
    await session.execute(stmp)
    await session.commit()
