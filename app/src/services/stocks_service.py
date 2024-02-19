import pandas as pd

from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import warehouse_db as db
from src.database import offer_db
import src.services.offer_utils as utils
from src.database.settings_db import get_markets
from src.schemas.offer_schemas import OfferOut
from src.schemas.stocks_schemas import WarehouseCreate, WarehouseOut, OfferStockOut, OfferStockCreate, \
    OfferWithStocksUpdate, OwnStorageCreate, OwnStorageUpdate
from src.services.base_utils import error_handler

api_wrapper = APIWrapper()


async def update_warehouses_and_stocks():
    stocks = await api_wrapper.get_stocks()

    async with async_session() as session:
        for warehouse in stocks:
            warehouse_db, _ = await db.update_or_create_warehouse(session, WarehouseCreate(
                    name=warehouse.name,
                    warehouse_id_in_marketplace=warehouse.warehouse_id,
                    market=warehouse.market
                ))

            for offer in await offer_db.get_offers(session, {'market': warehouse.market}):
                stock, created = await db.get_or_create_offer_stocks(session, OfferStockCreate(
                    current_stock=0,
                    warehouse_id=warehouse_db.id,
                    offer_id=offer.id
                ))

            for offer_stock in warehouse.offers:
                offer = await offer_db.get_offer(session, {'sku': offer_stock.sku, 'name_of_shop': offer_stock.name_of_shop, 'market': warehouse.market})

                offer_stock_create = OfferStockCreate(
                    current_stock=offer_stock.current_stock,
                    warehouse_id=warehouse_db.id,
                    offer_id=offer.id
                )
                await db.update_or_create_offer_stock(session, offer_stock_create)


        # for warehouse in stocks:
        #     warehouse_db, _ = await db.update_or_create_warehouse(session, WarehouseCreate(
        #         name=warehouse.name,
        #         warehouse_id_in_marketplace=warehouse.warehouse_id,
        #         market=warehouse.market
        #     ))
        #
        #     for offer_stock in warehouse.offers:
        #         offer = await offer_db.get_offer(session, {'sku': offer_stock.sku, 'name_of_shop': offer_stock.name_of_shop, 'market': warehouse.market})
        #
        #         offer_stock_create = OfferStockCreate(
        #             current_stock=offer_stock.current_stock,
        #             warehouse_id=warehouse_db.id,
        #             offer_id=offer.id
        #         )
        #         await db.update_or_create_offer_stock(session, offer_stock_create)

        for sku in await offer_db.get_unique_skus(session):
            await db.update_or_create_own_storage(session, OwnStorageCreate(sku=sku))


async def get_warehouses():
    async with async_session() as session:
        return await db.get_warehouses(session)


async def get_offers_stocks():
    async with async_session() as session:
        return await db.get_offers_stocks(session)


@error_handler('Не удалось получить остатки с магазинов.')
async def get_offers_with_stocks():
    async with async_session() as session:
        return await db.get_offers_with_stocks(session)


@error_handler('Не удалось обновить остатки с магазинов.')
async def change_offer_with_stock(data: list[OfferWithStocksUpdate]):
    async with async_session() as session:
        await db.change_offer_with_stock(session, data)


@error_handler('Не удалось получить собственные остатки.')
async def get_own_storages():
    async with async_session() as session:
        storages = await db.get_own_storages(session)
        markets = await get_markets(session)
        return {'markets': markets, 'data': storages}


@error_handler('Не удалось обновить собственные остатки.')
async def change_own_storages(data: list[OwnStorageUpdate]):
    async with async_session() as session:
        await db.change_own_storages(session, data)


@error_handler('Ошибка импорта остатков магазинов.')
async def import_offers_stocks(data, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df[['note_1', 'note_2', 'note_3']] = df[['note_1', 'note_2', 'note_3']].fillna('')

    if name_of_shop:
        df = df[df['name_of_shop'] == name_of_shop]

    if market:
        df = df[df['market'] == market]

    # Выбираем изменяемые колонки
    stocks_df = df[[i for i in df.columns.values[10:].tolist() if 'мин. остаток' in i]]
    df = df[df.columns.values[:10]]

    async with async_session() as session:
        warehouse_columns = [i.split(', ')[:2] for i in stocks_df.columns.values]
        warehouse_columns = [i.id for i in await db.get_warehouses_by_name_and_market(session, warehouse_columns)]

        # колонки остатков теперь имеют id склада
        stocks_df.columns = warehouse_columns

        df = pd.concat([df, stocks_df], axis=1)

        to_update = []

        for row in df.iterrows():
            offer_series = row[1][0:10]
            stocks_series = row[1][10:]

            offer_stocks = []
            for warehouse_id, min_stock in stocks_series.to_dict().items():
                offer_stock = await db.get_offer_stock(session, offer_series['id'], warehouse_id)

                if offer_stock:
                    offer_stocks.append(
                        {'id': offer_stock.id, 'min_stock': min_stock}
                    )

            offer_data = {
                'id': offer_series['id'],
                'note_1': offer_series['note_1'],
                'note_2': offer_series['note_2'],
                'note_3': offer_series['note_3'],
                'hidden': offer_series['hidden'],
                'stocks': offer_stocks
            }
            to_update.append(offer_data)

        await db.change_offer_with_stock(session, [OfferWithStocksUpdate(**i) for i in to_update])


@error_handler('Ошибка экспорта остатков магазинов.')
async def export_stocks(name_of_shop: str | None = None, market: str | None = None) -> str:
    offers_with_stocks = await get_offers_with_stocks()
    warehouses = await get_warehouses()
    warehouse_columns = []
    for warehouse in warehouses:
        base_name = f'{warehouse.name}, {warehouse.market}'
        warehouse_columns.append(f'{base_name}, в наличии')
        warehouse_columns.append(f'{base_name}, мин. остаток')
        warehouse_columns.append(f'{base_name}, к поставке')

    df = pd.DataFrame([i.model_dump() for i in offers_with_stocks])
    df[warehouse_columns] = 0

    stocks = df.pop('stocks').values.tolist()

    for index, offer in enumerate(stocks):
        for stock in offer:
            base_column_name = f"{stock['warehouse']['name']}, {stock['warehouse']['market']}"

            df.at[index, f'{base_column_name}, в наличии'] = stock['current_stock']
            df.at[index, f'{base_column_name}, мин. остаток'] = stock['min_stock']
            df.at[index, f'{base_column_name}, к поставке'] = stock['for_delivery']

    df['id'] = df['id'].astype(int)

    if name_of_shop:
        df = df[df['name_of_shop'] == name_of_shop]

    if market:
        df = df[df['market'] == market]

    df.rename(columns=OfferOut.fields(), inplace=True)
    df.to_excel('data/stocks-fbo.xlsx', index=False)
    return 'data/stocks-fbo.xlsx'


@error_handler('Ошибка экспорта собственных остатков.')
async def export_own_storages(name_of_shop: str | None = None, market: str | None = None) -> str:
    data = await get_own_storages()
    columns = ['sku', 'Название', 'Фото', 'Магазин', 'Маркетплейс', 'Примечание 1', 'Примечание 2', 'Примечание 3', 'Мои остатки']
    aggregated_columns = ['name', 'photo', 'name_of_shop', 'market', 'note_1', 'note_2', 'note_3']

    df = pd.DataFrame(data['data'])
    df[aggregated_columns] = df[aggregated_columns].applymap(lambda x: ', '.join([str(i) for i in x]))
    df['own_storage'] = df['own_storage'].apply(lambda x: x.value)

    stocks = df.pop('stocks').values.tolist()

    df.columns = columns

    stocks_columns = [f'{i.name} {i.type}' for i in data['markets']]
    df[stocks_columns] = 0

    for index, stocks_data in enumerate(stocks):
        for stock in stocks_data:
            col_name = f'{stock["name_of_shop"]} {stock["market"]}'
            df.at[index, col_name] = stock['value']

    df.to_excel('data/out-own-storages.xlsx', index=False)
    return 'data/out-own-storages.xlsx'


@error_handler('Ошибка импорта собственных остатков.')
async def import_own_storages(data, name_of_shop: str | None = None, market: str | None = None, file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df.rename(columns={'Мои остатки': 'value'}, inplace=True)
    df = df[['sku', 'value']]

    data = df.to_dict('records')

    async with async_session() as session:
        await db.update_own_storages_by_sku(session, data)


