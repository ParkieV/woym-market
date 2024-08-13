from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func, text, bindparam, literal_column, Select, insert, cast, \
    String, case
from sqlalchemy.orm import selectinload, subqueryload, Load, joinedload, load_only, contains_eager
from src.database.utils import _update_or_create_object, _get_or_create
from src.schemas.base_api_schemas import WarehouseType
from src.schemas.stocks.own_storages_schemas import OwnStorageAggOfferOut, OwnStorageOfferStockOut, OwnStorageOut, \
    OwnStorageCreate, OwnStorageStockOut, OwnStorageUpdate, OwnStoragePlaceCreate, OwnStoragePlaceOut, \
    OwnStoragePlaceUpdate
from src.schemas.stocks.stocks_schemas import SupplyData, GeneralOrderData
from src.schemas.stocks.fbo_schemas import OfferStockUpdate, OfferStockCreate, OfferStockOut, \
    OfferStockWithWarehouseOut, OfferWithStocks, OfferWithStocksUpdate
from src.schemas.stocks.warehouses_schemas import WarehouseCreate, WarehouseOut
from src.database.models.models import Warehouse, OfferStock, OwnStorage, OwnStoragePlace, Market
from pydantic import BaseModel
from src.database.models.models import Offer
from typing import Type, TypeVar, Any
from fastapi import status
from fastapi.exceptions import HTTPException
from collections import defaultdict

ModelSchema = TypeVar('ModelSchema', bound=Type[BaseModel])


remaining_stocks_subuery = (
    select(
        OfferStock.offer_id,
        func.sum(OfferStock.for_delivery).label('remaining_stock')
    )
    .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
    .where(Warehouse.warehouse_type == WarehouseType.WAREHOUSE)
    .group_by(
        OfferStock.offer_id).subquery())


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


async def get_all_offers_stocks(session: AsyncSession):
    query = (
        select(
            OfferStock.id.label('id'),
            OfferStock.current_stock,
            OfferStock.offer_id,
            Warehouse.name.label('warehouse_name'),
            Offer.sku.label('sku'),
            Offer.market.label('market'),
            Offer.name_of_shop.label('name_of_shop'),
        )
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .join(Offer, Offer.id == OfferStock.offer_id)
    )
    result = (await session.execute(query)).all()
    return result


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


# min_stock: int
# in_box: int
# is_deliver_in_boxes: bool

async def change_offer_with_stock(session: AsyncSession, data: list[OfferWithStocksUpdate]) -> None:
    for offer_with_stock in data:
        offer_data = offer_with_stock.model_dump()
        offer_data.pop('stocks')

        stmp = update(Offer).where(Offer.id == offer_data['id']).values(**offer_data)
        await session.execute(stmp)

        for stock in offer_with_stock.stocks:
            in_box_expr = case(
                (stock.is_deliver_in_boxes, stock.in_box),
                else_=1
            )

            for_delivery_expr = case(
                (stock.min_stock > OfferStock.current_stock,
                 func.ceil(
                     (stock.min_stock - OfferStock.current_stock) /
                     func.nullif(in_box_expr, 0)
                 ) * in_box_expr),
                else_=0
            )

            stmp = update(OfferStock).where(OfferStock.id == stock.id).values(
                in_box=stock.in_box,
                min_stock=stock.min_stock,
                for_delivery=for_delivery_expr,
                is_deliver_in_boxes=stock.is_deliver_in_boxes,
            )
            await session.execute(stmp)

    await session.commit()


async def recalculate_stocks_for_delivery(session: AsyncSession) -> None:
    in_box_expr = case(
        (OfferStock.is_deliver_in_boxes, OfferStock.in_box),
        else_=1
    )

    for_delivery_expr = case(
        (OfferStock.min_stock > OfferStock.current_stock,
         func.ceil(
             (OfferStock.min_stock - OfferStock.current_stock) /
             func.nullif(in_box_expr, 0)
         ) * in_box_expr),
        else_=0
    )

    stmp = update(OfferStock).values(
        for_delivery=for_delivery_expr,
    )
    await session.execute(stmp)


async def update_or_create_warehouse(session: AsyncSession, data: WarehouseCreate) -> (WarehouseOut, bool):
    return await _update_or_create_object(
        session,
        Warehouse,
        data,
        and_(Warehouse.market == data.market, Warehouse.name == data.name),
        WarehouseOut
    )


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


async def get_own_storages(session: AsyncSession, place_id: int | None = None) -> list[OwnStorageOut]:
    agg_offers_query = (
        select(
            Offer.sku,
            func.array_agg(Offer.name.distinct()).label('name'),
            func.array_agg(Offer.photo.distinct()).label('photo'),
            func.array_agg(Offer.name_of_shop.distinct()).label('name_of_shop'),
            func.array_agg(Offer.market.distinct()).label('market'),
            func.array_agg(Offer.note_1.distinct()).label('note_1'),
            func.array_agg(Offer.note_2.distinct()).label('note_2'),
            func.array_agg(Offer.note_3.distinct()).label('note_3'),
            func.array_agg(Offer.barcodes.distinct()).label('barcodes'),
        )
        .group_by(Offer.sku)
    )

    agg_offers_result = [OwnStorageAggOfferOut.model_validate(i, from_attributes=True) for i in
                         (await session.execute(agg_offers_query)).all()]

    offer_stocks_query = (
        select(
            OfferStock.offer_id,
            Offer.sku,
            Offer.market,
            Offer.name_of_shop,
            func.coalesce(func.sum(OfferStock.current_stock), 0).label('stock')
        )
        .join(Offer, Offer.id == OfferStock.offer_id)
        .group_by(OfferStock.offer_id, Offer.sku, Offer.market, Offer.name_of_shop)
    )

    offer_stocks_result = [OwnStorageOfferStockOut.model_validate(i, from_attributes=True) for i in
                           (await session.execute(offer_stocks_query)).all()]
    stocks = defaultdict(list)
    for offer_stock in offer_stocks_result:
        stocks[offer_stock.sku].append(offer_stock)

    own_storages = select(OwnStorage)
    if place_id is not None:
        own_storages = own_storages.where(OwnStorage.storage_place_id == place_id)

    own_storages_result = [OwnStorageStockOut.model_validate(i, from_attributes=True) for i in
                           (await session.execute(own_storages)).scalars()]

    own_storages = defaultdict(list)
    for own_storage in own_storages_result:
        own_storages[own_storage.sku].append(own_storage)

    return [
        OwnStorageOut(
            offer=offer,
            storages=own_storages[offer.sku],
            stocks=stocks[offer.sku],
        )
        for offer in agg_offers_result
    ]


async def change_own_storages(session: AsyncSession, data: list[OwnStorageUpdate]):
    for storage in data:
        stmp = update(OwnStorage).where(OwnStorage.id == storage.id).where(
            OwnStorage.storage_place_id == storage.storage_place_id).values(**storage.model_dump())
        await session.execute(stmp)

    await session.commit()


async def increment_own_storage_values(session: AsyncSession, data: list[dict[str, Any]], place_id: int):
    for item in data:
        stmp = update(OwnStorage).where(OwnStorage.storage_place_id == place_id).where(
            OwnStorage.sku == item['sku']).values(value=OwnStorage.value + item['value'])
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
        stmp = update(OwnStorage).where(OwnStorage.storage_place_id == place_id).where(
            OwnStorage.sku == storage['sku']).values(**storage)
        await session.execute(stmp)

    await session.commit()


async def get_supply_data(
        session: AsyncSession,
        warehouses: list[int],
        offers: list[int],
        place_id: int = None,
):
    query = (
        select(Offer.sku, Offer.name, Offer.name_of_shop, Offer.market, OfferStock.for_delivery,
               Warehouse.name.label('warehouse_name'),
               OwnStorage.value.label('own_storage_value'),
               Offer.barcodes,
               Offer.current_price)
        .join(Offer, OfferStock.offer_id == Offer.id)
        .join(Warehouse, OfferStock.warehouse_id == Warehouse.id)
        .outerjoin(OwnStorage, OwnStorage.sku == Offer.sku)
        .where(OfferStock.offer_id.in_(offers))
        .where(Warehouse.id.in_(warehouses))
    )
    if place_id is not None:
        query = query.where(OwnStorage.storage_place_id == place_id)

    result = await session.execute(query)
    return [
        SupplyData.model_validate(i, from_attributes=True) for i in result.all()
    ]


async def get_supply_only_stocks(session: AsyncSession, warehouses: list[int], offers: list[int], place_id: int):
    offers_query = (
        select(
            Offer.sku,
            Offer.name,
            Offer.name_of_shop,
            Offer.market,
            Offer.name_of_shop,
            Offer.barcodes,
            Offer.current_price,
            Offer.volume,
            Offer.self_weight,
            Offer.cost_price,
            OfferStock.for_delivery,
            Warehouse.name.label('warehouse_name'),
            OfferStock.for_delivery.label('base_for_delivery')
        )
        .join(OfferStock, OfferStock.offer_id == Offer.id)
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .where(Warehouse.id.in_(warehouses))
        .where(Offer.id.in_(offers)))

    aggregated_offers_query = select(
        offers_query.c.sku,
        func.string_agg(offers_query.c.name, literal_column("','")).label('name'),
        func.avg(offers_query.c.current_price).label('current_price'),
        func.sum(offers_query.c.for_delivery).label('for_delivery'),
        func.avg(offers_query.c.volume).label('volume'),
        func.avg(offers_query.c.self_weight).label('self_weight'),
        func.avg(offers_query.c.cost_price).label('cost_price'),
        func.sum(offers_query.c.base_for_delivery).label('base_for_delivery')
    ).group_by(offers_query.c.sku)

    offers_result = (await session.execute(offers_query)).all()
    aggregated_offers_result = (await session.execute(aggregated_offers_query)).all()

    return (
        [SupplyData.model_validate(i, from_attributes=True) for i in offers_result],
        [GeneralOrderData.model_validate(i, from_attributes=True) for i in aggregated_offers_result])


async def get_supply_only_own_storage(session: AsyncSession, warehouses: list[int], offers: list[int], place_id: int):
    own_storage_query = (select(OwnStorage.value).where(OwnStorage.storage_place_id == place_id).where(
        OwnStorage.sku == Offer.sku)).label('own_storage_value')

    offers_query = (
        select(
            Offer.sku,
            Offer.name,
            Offer.name_of_shop,
            Offer.market,
            Offer.name_of_shop,
            Offer.barcodes,
            Offer.current_price,
            Offer.volume,
            Offer.self_weight,
            Offer.cost_price,
            Warehouse.name.label('warehouse_name'),
            func.greatest(0, func.least(OfferStock.for_delivery, (own_storage_query - func.coalesce(
                func.sum(OfferStock.for_delivery).over(partition_by=Offer.sku, order_by=OfferStock.for_delivery.desc(),
                                                       rows=(None, -1)), 0)))).label('for_delivery'),
            OfferStock.for_delivery.label('base_for_delivery')
        )
        .join(OfferStock, OfferStock.offer_id == Offer.id)
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .where(Warehouse.id.in_(warehouses))
        .where(Offer.id.in_(offers))
    )

    aggregated_offers_query = select(
        offers_query.c.sku,
        func.string_agg(offers_query.c.name, literal_column("','")).label('name'),
        func.avg(offers_query.c.current_price).label('current_price'),
        func.sum(offers_query.c.for_delivery).label('for_delivery'),
        func.avg(offers_query.c.volume).label('volume'),
        func.avg(offers_query.c.self_weight).label('self_weight'),
        func.avg(offers_query.c.cost_price).label('cost_price'),
        (select(OwnStorage.value).where(OwnStorage.storage_place_id == place_id).where(
            OwnStorage.sku == offers_query.c.sku)).label('own_storage_value'),
        func.sum(offers_query.c.base_for_delivery).label('base_for_delivery')
    ).group_by(offers_query.c.sku)

    offers_result = (await session.execute(offers_query)).all()
    aggregated_offers_result = (await session.execute(aggregated_offers_query)).all()

    return (
        [SupplyData.model_validate(i, from_attributes=True) for i in offers_result],
        [GeneralOrderData.model_validate(i, from_attributes=True) for i in aggregated_offers_result])


async def get_general_order_data(
        session: AsyncSession,
        warehouses: list[int],
        offers: list[int],
        place_id: int | None = None,
):
    for_delivery_query = (
        select(func.sum(OfferStock.for_delivery))
        .where(OfferStock.offer_id == Offer.id)
        .where(OfferStock.warehouse_id.in_(warehouses))
    )

    tb = select(
        Offer.sku,
        Offer.name,
        Offer.volume,
        Offer.cost_price,
        Offer.self_weight,
        for_delivery_query.label('for_delivery'),
    ).where(Offer.id.in_(offers))

    own_storage_value = (
        select(OwnStorage.value)
        .where(OwnStorage.sku == tb.c.sku)
        .where(OwnStorage.storage_place_id == place_id)
    )

    query = select(
        tb.c.sku,
        func.string_agg(tb.c.name, literal_column("','")).label('name'),
        func.avg(tb.c.volume).label('volume'),
        func.avg(tb.c.cost_price).label('cost_price'),
        func.avg(tb.c.self_weight).label('self_weight'),
        func.sum(tb.c.for_delivery).label('for_delivery'),
        func.sum(own_storage_value).label('own_storage_value'),
    ).group_by(tb.c.sku)

    result = (await session.execute(query)).all()

    return [GeneralOrderData.model_validate(i, from_attributes=True) for i in result]


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


async def get_warehouse(session: AsyncSession, warehouse_id: int, model_schema: Type[ModelSchema] = WarehouseOut,
                        allow_none: bool = True) -> WarehouseOut | None:
    query = select(Warehouse).where(Warehouse.id == warehouse_id)
    result = (await session.execute(query)).scalar_one_or_none()

    if not result:
        if allow_none:
            return None

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Warehouse with id - {warehouse_id} not found")

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


async def get_own_storage_place(session: AsyncSession, place_id: int, allow_none: bool = False) -> OwnStoragePlaceOut | None:
    query = select(OwnStoragePlace).where(OwnStoragePlace.id == place_id)
    result = (await session.execute(query)).scalar_one_or_none()

    if not result:
        if allow_none:
            return None
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f'Моего склада с id - {place_id} не найдено')

    return OwnStoragePlaceOut.model_validate(result, from_attributes=True)


async def change_own_storage_places(session: AsyncSession, data: list[OwnStoragePlaceUpdate]):
    for place in data:
        stmp = update(OwnStoragePlace).where(OwnStoragePlace.id == place.id).values(**place.model_dump())
        await session.execute(stmp)

    await session.commit()


async def create_fbo_stocks_(session: AsyncSession, data: list[dict]):
    for item in data:
        warehouse_id_query = select(Warehouse.id).where(Warehouse.name == item["warehouse_name"])
        warehouse_id_rez = (await session.execute(warehouse_id_query)).first()

        if not warehouse_id_rez:
            continue

        offer_id_query = select(Offer.id).where(
            and_(Offer.sku == item['sku'], Offer.market == item['market'], Offer.name_of_shop == item['name_of_shop']))
        offer_id_rez = (await session.execute(offer_id_query)).first()

        if not offer_id_rez:
            continue

        stmp = insert(OfferStock).values(
            offer_id=offer_id_rez[0],
            current_stock=item['current_stock'],
            warehouse_id=warehouse_id_rez[0],
        )
        await session.execute(stmp)

        await session.commit()


async def update_fbo_stocks(session: AsyncSession, data: list[dict]):
    for stock in data:
        stmp = update(OfferStock).values(current_stock=stock['current_stock']).where(OfferStock.id == stock['id'])
        await session.execute(stmp)

    await session.commit()


async def fill_empty_stocks(session: AsyncSession):
    markets_query = select(
        func.upper(cast(Market.type, String)).label('market'),
        func.array(
            (select(Warehouse.id).where(
                func.upper(cast(Warehouse.market, String)) == func.upper(cast(Market.type, String))))
        ).label('warehouses')
    )
    markets_warehouses = {i.market: set(i.warehouses) for i in (await session.execute(markets_query)).all()}

    query = select(
        Offer.id,
        Offer.sku,
        func.upper(cast(Offer.market, String)).label('market'),
        Offer.name_of_shop,
        func.array(
            (select(OfferStock.warehouse_id).where(OfferStock.offer_id == Offer.id))
        ).label('warehouses')
    )
    result = (await session.execute(query)).all()

    for item in result:
        if len(markets_warehouses[item.market]) == len(set(item.warehouses)):
            continue

        to_set_warehouses_stocks = markets_warehouses[item.market] - set(item.warehouses)

        new_stocks = [OfferStock(offer_id=item.id, warehouse_id=warehouse_id, current_stock=0) for warehouse_id in
                      to_set_warehouses_stocks]
        session.add_all(new_stocks)

        await session.commit()


async def get_fbo_offers(session: AsyncSession):
    # 6359 ms

    # query = (
    #             select(Offer)
    #             .options(subqueryload(Offer.stocks).selectinload(OfferStock.warehouse))
    #         )
    # result = await session.execute(query)
    # offers = result.scalars().all()
    # return [OfferWithStocks.model_validate(i, from_attributes=True) for i in offers]

    chunck_size = 1000
    offset = 0
    results = []

    while True:
        print(offset)
        query = (
            select(Offer)
            .options(subqueryload(Offer.stocks).selectinload(OfferStock.warehouse))
        ).offset(offset).limit(chunck_size)
        result = await session.execute(query)
        offers = result.scalars().all()

        results.extend([OfferWithStocks.model_validate(i, from_attributes=True) for i in offers])

        if len(offers) < chunck_size:
            break

        offset += chunck_size

    return results


async def get_offer_stocks(session: AsyncSession, offer_id: int):
    query = (
        select(OfferStock)
        .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
        .options(selectinload(OfferStock.warehouse))
        .order_by(Warehouse.warehouse_type.asc())
        .order_by(Warehouse.name.asc())
        .where(OfferStock.offer_id == offer_id)
    )
    result = (await session.execute(query)).scalars()
    return [OfferStockWithWarehouseOut.model_validate(i, from_attributes=True) for i in result]
