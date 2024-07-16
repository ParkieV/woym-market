from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func, text, bindparam, literal_column, Select
from sqlalchemy.orm import selectinload, subqueryload
from src.database.utils import _update_or_create_object, _get_or_create
from src.schemas.stocks_schemas import WarehouseCreate, OfferStockCreate, WarehouseOut, OfferStockOut, OfferWithStocks, \
    OfferStockWithWarehouseOut, OfferWithStocksUpdate, OfferStockUpdate, OwnStorageCreate, OwnStorageOut, \
    OwnStorageUpdate, SupplyData, GeneralOrderData, OwnStoragePlaceCreate, OwnStoragePlaceOut, OwnStoragePlaceUpdate
from src.database.models.models import Warehouse, OfferStock, OwnStorage, OwnStoragePlace
from pydantic import BaseModel
from src.database.models.models import Offer
from typing import Type, TypeVar, Any
from fastapi import status
from fastapi.exceptions import HTTPException

ModelSchema = TypeVar('ModelSchema', bound=Type[BaseModel])


async def create_warehouse(session: AsyncSession, data: WarehouseCreate,
                           model_schema: ModelSchema = WarehouseOut) -> ModelSchema:
    warehouse_db = Warehouse(**data.model_dump())
    session.add(warehouse_db)
    await session.commit()
    return model_schema.model_validate(warehouse_db, from_attributes=True)


async def get_warehouses(session: AsyncSession, model_schema: ModelSchema = WarehouseOut) -> list[ModelSchema]:
    query = select(Warehouse)
    result = await session.execute(query)
    return [model_schema.model_validate(warehouse_db, from_attributes=True) for warehouse_db in result.scalars().all()]


async def create_offer_stock(session: AsyncSession, data: OfferStockCreate,
                             model_schema: ModelSchema = OfferStockOut) -> ModelSchema:
    offer_stock_db = OfferStock(**data.model_dump())
    session.add(offer_stock_db)
    await session.commit()
    return model_schema.model_validate(offer_stock_db, from_attributes=True)


async def get_offers_stocks(session: AsyncSession, model_schema: ModelSchema = OfferStockWithWarehouseOut) -> list[
    ModelSchema]:
    query = select(OfferStock).where(OfferStock.offer_id == 1).options(selectinload(OfferStock.warehouse))
    result = await session.execute(query)
    return [model_schema.model_validate(offer_stock_db, from_attributes=True) for offer_stock_db in
            result.scalars().all()]


async def get_offer_stock_by_id(session: AsyncSession, _id: int,
                                model_schema: ModelSchema = OfferStockOut) -> ModelSchema:
    query = select(OfferStock).where(OfferStock.id == _id)
    result = await session.execute(query)
    return model_schema.model_validate(result.scalar_one(), from_attributes=True)


async def get_offers_with_stocks(session: AsyncSession, model_schema: ModelSchema = OfferWithStocks) -> list[
    ModelSchema]:
    query = (
        select(Offer)
        .options(subqueryload(Offer.stocks).subqueryload(OfferStock.warehouse))
    )
    result = await session.execute(query)
    return [model_schema.model_validate(offer, from_attributes=True) for offer in result.scalars().all()]


def count_delivery_items(in_stock: int, in_box: int, min_stock: int):
    if min_stock < in_stock:
        return 0
    to_order_sht = min_stock - in_stock
    ost = 1 if (to_order_sht % in_box) else 0
    box_to_order = (to_order_sht // in_box) + ost
    return box_to_order * in_box


async def change_offer_with_stock(session: AsyncSession, data: list[OfferWithStocksUpdate]):
    for offer_with_stock in data:
        offer_data = offer_with_stock.model_dump()
        offer_data.pop('stocks')

        stmp = update(Offer).where(Offer.id == offer_data['id']).values(**offer_data)
        await session.execute(stmp)

        for stock in offer_with_stock.stocks:
            db_stock: OfferStockOut = await get_offer_stock_by_id(session, stock.id)

            in_box = stock.in_box if stock.is_deliver_in_boxes else 1
            for_delivery = count_delivery_items(db_stock.current_stock, in_box, stock.min_stock)

            stock_data = stock.model_dump()
            stmp = update(OfferStock).where(OfferStock.id == stock_data['id']).values(for_delivery=for_delivery,
                                                                                      **stock_data)
            await session.execute(stmp)

    await session.commit()


async def update_or_create_warehouse(session: AsyncSession, data: WarehouseCreate) -> (WarehouseOut, bool):
    return await _update_or_create_object(
        session,
        Warehouse,
        data,
        and_(Warehouse.market == data.market, Warehouse.name == data.name),
        WarehouseOut
    )


async def update_or_create_offer_stock(session: AsyncSession, data: OfferStockCreate):
    query = select(OfferStock).where(
        and_(OfferStock.offer_id == data.offer_id, OfferStock.warehouse_id == data.warehouse_id)).distinct()
    result = await session.execute(query)
    object_db = result.scalar_one_or_none()

    if object_db is None:
        object_db = OfferStock(**data.model_dump())
        session.add(object_db)
    else:
        stmp = (
            update(OfferStock)
            .where(and_(OfferStock.offer_id == data.offer_id, OfferStock.warehouse_id == data.warehouse_id))
            .values(**data.model_dump())
        )
        await session.execute(stmp)
    await session.commit()


async def relate_warehouses_with_clusters(session: AsyncSession, storages: list[dict]):
    for storage in storages:
        if not storage['related_warehouses_name']:
            continue

        stmp = (
            update(Warehouse).where(Warehouse.name.in_(storage['related_warehouses_name'])).where(
                Warehouse.market == 'ozon')
            .values(parent_warehouse_id=(
                select(Warehouse.id).where(Warehouse.market == 'ozon').where(Warehouse.name == storage['name'])))
        )
        await session.execute(stmp)

    stmp = text("""update offers_stocks as stock set current_stock = (
            select sum(offers_stocks.current_stock) from offers_stocks
            join warehouses on offers_stocks.warehouse_id = warehouses.id
            where warehouses.parent_warehouse_id = cluster.id and offer_id = stock.offer_id
            ) from warehouses as cluster
            where cluster.warehouse_type = 'cluster' and stock.warehouse_id = cluster.id
            """)
    await session.execute(stmp)

    stmp = update(OfferStock).options(selectinload(OfferStock.warehouse)).where(
        Warehouse.warehouse_type == 'cluster').where(OfferStock.current_stock == None).values(current_stock=0)

    await session.execute(stmp)
    await session.commit()


async def update_or_create_own_storage(session: AsyncSession, data: OwnStorageCreate):
    query = select(OwnStorage).where(OwnStorage.sku == data.sku).distinct()
    result = await session.execute(query)
    object_db = result.scalar_one_or_none()

    if object_db is None:
        object_db = OwnStorage(**data.model_dump())
        session.add(object_db)
    else:
        stmp = (
            update(OwnStorage)
            .where(OwnStorage.sku == data.sku)
            .values(**data.model_dump())
        )
        await session.execute(stmp)
    await session.commit()


async def get_own_storages(session: AsyncSession, place_id: int | None):
    storages_result = []

    skus_query = await session.execute(select(Offer.sku).distinct())

    for sku in skus_query.all():
        offers_query = await session.execute(
            select(Offer, OwnStorage).where(Offer.sku == sku[0]).join(OwnStorage, OwnStorage.sku == Offer.sku, isouter=True).where(OwnStorage.storage_place_id == place_id)
        )

        data = {
            'sku': sku[0],
            'name': set(),
            'photo': set(),
            'name_of_shop': set(),
            'market': set(),
            'note_1': set(),
            'note_2': set(),
            'note_3': set(),
            'stocks': []
        }

        for offer, own_storage in offers_query.all():
            if not own_storage: continue

            data['name'].add(offer.name)
            data['photo'].add(offer.photo)
            data['note_1'].add(offer.note_1)
            data['note_2'].add(offer.note_2)
            data['note_3'].add(offer.note_3)
            data['name_of_shop'].add(offer.name_of_shop)
            data['market'].add(offer.market)
            data['own_storage'] = OwnStorageOut.model_validate(own_storage, from_attributes=True)
            data['stocks'].append(
                {
                    'name_of_shop': offer.name_of_shop,
                    'market': offer.market,
                    'value': offer.remaining_stock
                }
            )

        if 'own_storage' not in data: continue

        storages_result.append(data)

    return storages_result




async def change_own_storages(session: AsyncSession, data: list[OwnStorageUpdate]):
    for storage in data:
        stmp = update(OwnStorage).where(OwnStorage.id == storage.id).where(OwnStorage.storage_place_id == storage.storage_place_id).values(**storage.model_dump())
        await session.execute(stmp)

    await session.commit()


async def increment_own_storage_values(session: AsyncSession, data: list[dict[str, Any]], place_id: int):
    for item in data:
        stmp = update(OwnStorage).where(OwnStorage.storage_place_id == place_id).where(OwnStorage.sku == item['sku']).values(value=OwnStorage.value + item['value'])
        await session.execute(stmp)
    await session.commit()


async def get_or_create_offer_stocks(session: AsyncSession, data: OfferStockCreate):
    return await _get_or_create(
        session,
        OfferStock,
        data,
        and_(OfferStock.offer_id == data.offer_id,
             OfferStock.warehouse_id == data.warehouse_id),
        OfferStockOut
    )


#
# async def get_offer_stock_by(session: AsyncSession, offer_id: int, warehouse_name: str, warehouse_market: str):
#     warehouse_query = select(Warehouse).where(Warehouse.name==warehouse_name).where(Warehouse.market==warehouse_market)
#     result = await session.execute(warehouse_query)
#     warehouse_db = result.scalar_one_or_none()
#
#     if warehouse_db is None:
#         return None
#
#     stock_query = select(OfferStock).where(OfferStock.offer_id==offer_id).where(OfferStock.warehouse_id==warehouse_db.id)
#     result = await session.execute(stock_query)
#     return result.scalar_one_or_none()


async def get_warehouses_by_name_and_market(session: AsyncSession, data: list[list[str, str]]) -> list[WarehouseOut]:
    results = []

    for i in data:
        query = select(Warehouse).where(and_(Warehouse.name == i[0], Warehouse.market == i[1]))
        warehouse_db = (await session.execute(query)).scalar_one_or_none()

        if warehouse_db is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Некоректные данные для определения склада')

        results.append(WarehouseOut.model_validate(warehouse_db, from_attributes=True))

    return results


async def get_offer_stock(session: AsyncSession, offer_id: int, warehouse_id: int):
    query = select(OfferStock).where(OfferStock.offer_id == offer_id).where(OfferStock.warehouse_id == warehouse_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_own_storages_by_sku(session: AsyncSession, data: list[dict], place_id: int):
    for storage in data:
        stmp = update(OwnStorage).where(OwnStorage.storage_place_id == place_id).where(OwnStorage.sku == storage['sku']).values(**storage)
        await session.execute(stmp)

    await session.commit()


async def get_supply_data(session: AsyncSession, warehouses: list[int] | None = None, offers: list[int] | None = None, market: str | None = None, name_of_shop: str | None = None):
    query = (
        select(Offer.sku, Offer.name, Offer.name_of_shop, Offer.market, OfferStock.for_delivery, Warehouse.name.label('warehouse_name'),
               Offer.supplier_available, OwnStorage.value.label('own_storage_value'), Offer.barcodes, Offer.current_price)
        .join(Offer, OfferStock.offer_id == Offer.id)
        .join(Warehouse, OfferStock.warehouse_id == Warehouse.id)
        .join(OwnStorage, OwnStorage.sku == Offer.sku)
        .where(OfferStock.offer_id.in_(offers))
        .where(Warehouse.id.in_(warehouses))
    )
    if market:
        query = query.where(Offer.market == market)

    if name_of_shop:
        query = query.where(Offer.name_of_shop == name_of_shop)

    result = await session.execute(query)
    return [
        SupplyData(
            sku=i[0],
            name=i[1],
            name_of_shop=i[2],
            market=i[3],
            for_delivery=i[4],
            warehouse_name=i[5],
            supplier_available=i[6],
            own_storage_value=i[7],
            barcodes=i[8],
            current_price=i[9]
        )
        for i in result.all()
    ]


async def get_general_order_data(session: AsyncSession, warehouses: list[int] | None = None, offers: list[int] | None = None, name_of_shop: str | None = None, market: str | None = None):
    for_delivery_query = select(func.sum(OfferStock.for_delivery)).where(OfferStock.offer_id == Offer.id)

    if warehouses:
        for_delivery_query = for_delivery_query.where(OfferStock.warehouse_id.in_(warehouses))

    tb = select(
        Offer.sku,
        Offer.name,
        Offer.volume,
        Offer.cost_price,
        Offer.self_weight,
        for_delivery_query.label('for_delivery'),
    )

    if market:
        tb = tb.where(Offer.market == market)

    if name_of_shop:
        tb = tb.where(Offer.name_of_shop == name_of_shop)

    if offers:
        tb = tb.where(Offer.id.in_(offers))

    query = select(
        tb.c.sku,
        func.string_agg(tb.c.name, literal_column("','")),
        func.avg(tb.c.volume),
        func.avg(tb.c.cost_price),
        func.avg(tb.c.self_weight),
        func.sum(tb.c.for_delivery)
    ).group_by(tb.c.sku)

    result = (await session.execute(query)).all()

    dt = [GeneralOrderData(
        sku=i[0],
        name=i[1],
        volume=i[2],
        cost_price=i[3],
        self_weight=i[4],
        for_delivery=i[5]
    ) for i in result]
    return dt


async def update_fbo_support_data(session: AsyncSession, data: list[dict], name_of_shop: str, warehouse_id: int):
    now = datetime.now()
    for stock in data:
        sub_query = (
            select(OfferStock.id)
            .join(Offer, Offer.id == OfferStock.offer_id)
            .where(OfferStock.warehouse_id == warehouse_id)
            .where(Offer.sku == str(stock['sku']))
        )

        stmp = update(OfferStock).where(OfferStock.id.in_(sub_query)).values(
            **{'can_be_delivered': stock['can_be_delivered'], 'advice_from_the_store': stock['advice_from_the_store']})
        await session.execute(stmp)
        stmp = update(Warehouse).where(Warehouse.id == warehouse_id).values(from_file_updated_at=now)
        await session.execute(stmp)

    await session.commit()


async def get_warehouse(session: AsyncSession, warehouse_id: int, model_schema: Type[ModelSchema] = WarehouseOut, allow_none: bool = True) -> WarehouseOut | None:
    query = select(Warehouse).where(Warehouse.id == warehouse_id)
    result = (await session.execute(query)).scalar_one_or_none()

    if not result:
        if allow_none:
            return None

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Warehouse with id - {warehouse_id} not found")

    return model_schema.model_validate(result, from_attributes=True)


async def create_own_storage_stocks(session: AsyncSession):
    places_query = select(OwnStoragePlace.id)
    places = [i[0] for i in (await session.execute(places_query)).all()]

    for place_id in places:
        sub_query = select(OwnStorage.sku).where(OwnStorage.storage_place_id == place_id).distinct()
        query = select(Offer.sku).distinct().where(Offer.sku.not_in(sub_query))
        result = (await session.execute(query)).all()
        skus = [i[0] for i in result]

        session.add_all([OwnStorage(sku=sku, value=0, storage_place_id=place_id) for sku in skus])
        await session.commit()


async def create_own_storage_places(session: AsyncSession, data: list[OwnStoragePlaceCreate]):
    db_storages = [OwnStoragePlace(**i.model_dump()) for i in data]
    session.add_all(db_storages)
    await session.commit()


async def get_all_own_storage_places(session: AsyncSession) -> list[OwnStoragePlaceOut]:
    query = select(OwnStoragePlace)
    result = await session.execute(query)
    return [OwnStoragePlaceOut.model_validate(i, from_attributes=True) for i in result.scalars()]


async def change_own_storage_places(session: AsyncSession, data: list[OwnStoragePlaceUpdate]):
    for place in data:
        stmp = update(OwnStoragePlace).where(OwnStoragePlace.id == place.id).values(**place.model_dump())
        await session.execute(stmp)

    await session.commit()
