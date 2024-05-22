import numpy as np
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from logs import get_logger
from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import warehouse_db as db
from src.database import offer_db
import src.services.offer_utils as utils
from src.database.settings_db import get_markets
from src.database.warehouse_db import get_general_order_data
from src.schemas.offer_schemas import OfferOut
from src.schemas.stocks_schemas import WarehouseCreate, WarehouseOut, OfferStockOut, OfferStockCreate, \
    OfferWithStocksUpdate, OwnStorageCreate, OwnStorageUpdate
from src.services.base_utils import error_handler, clean_up_files
from datetime import datetime
from pathlib import Path
from shutil import make_archive

api_wrapper = APIWrapper()

logger = get_logger(__name__)


async def update_warehouses_and_stocks():
    logger.info('Start update warehouses and stocks')
    start_time = datetime.now()

    stocks = await api_wrapper.get_stocks()

    async with async_session() as session:
        for warehouse in stocks:
            warehouse_db, _ = await db.update_or_create_warehouse(session, WarehouseCreate(
                name=warehouse.name,
                market=warehouse.market
            ))

            for offer in await offer_db.get_offers(session, {'market': warehouse.market}):
                stock, created = await db.get_or_create_offer_stocks(session, OfferStockCreate(
                    current_stock=0,
                    warehouse_id=warehouse_db.id,
                    offer_id=offer.id
                ))

            for offer_stock in warehouse.offers:
                offer = await offer_db.get_offer(session,
                                                 {'sku': offer_stock.sku, 'name_of_shop': offer_stock.name_of_shop,
                                                  'market': warehouse.market})

                offer_stock_create = OfferStockCreate(
                    current_stock=offer_stock.current_stock,
                    warehouse_id=warehouse_db.id,
                    offer_id=offer.id
                )
                await db.update_or_create_offer_stock(session, offer_stock_create)

        for sku in await offer_db.get_unique_skus(session):
            await db.update_or_create_own_storage(session, OwnStorageCreate(sku=sku))

    _time = datetime.now() - start_time
    logger.info(f'Warehouses and stocks updated completed in {_time}')


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
async def import_offers_stocks(data, name_of_shop: str | None = None, market: str | None = None,
                               file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df[['note_1', 'note_2', 'note_3']] = df[['note_1', 'note_2', 'note_3']].fillna('')

    if name_of_shop:
        df = df[df['name_of_shop'] == name_of_shop]

    if market:
        df = df[df['market'] == market]

    # Выбираем изменяемые колонки
    stocks_df = df[[i for i in df.columns.values[11:].tolist() if 'мин. остаток' in i]]
    df = df[df.columns.values[:11]]

    async with async_session() as session:
        warehouse_columns = [i.split(', ')[:2] for i in stocks_df.columns.values]
        warehouse_columns = [i.id for i in await db.get_warehouses_by_name_and_market(session, warehouse_columns)]

        # колонки остатков теперь имеют id склада
        stocks_df.columns = warehouse_columns

        df = pd.concat([df, stocks_df], axis=1)

        to_update = []

        for row in df.iterrows():
            offer_series = row[1][0:11]
            stocks_series = row[1][11:]

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
    columns = ['sku', 'Название', 'Фото', 'Магазин', 'Маркетплейс', 'Примечание 1', 'Примечание 2', 'Примечание 3',
               'Мои остатки']
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
async def import_own_storages(data, name_of_shop: str | None = None, market: str | None = None,
                              file_extension: str = 'xlsx'):
    df = utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df.rename(columns={'Мои остатки': 'value'}, inplace=True)
    df = df[['sku', 'value']]

    data = df.to_dict('records')

    async with async_session() as session:
        await db.update_own_storages_by_sku(session, data)


async def export_yandex_supply(data: pd.DataFrame, dir_path: Path):
    warehouses = set(data['warehouse_name'].values.tolist())

    for warehouse_name in warehouses:
        df = data[data['warehouse_name'] == warehouse_name]
        df = df[['sku', 'name', 'for_delivery', 'current_price', 'barcodes']]
        df.rename({
            'sku': 'Ваш SKU',
            'name': 'Название товара',
            'for_delivery': 'Количество товаров в поставке',
            'current_price': 'Объявленная ценность одного товара, руб.',
            'barcodes': 'Штрихкоды'
        }, axis='columns', inplace=True)
        file_path = dir_path / f'Склад {warehouse_name}, {datetime.now().strftime("%d.%m.%Y, %H:%M")}.xls'
        df.to_excel(file_path, index=False)


async def export_ozon_supply(data: pd.DataFrame, dir_path: Path):
    warehouses = set(data['warehouse_name'].values.tolist())

    for warehouse_name in warehouses:
        df = data[data['warehouse_name'] == warehouse_name]
        df = df[['sku', 'name', 'for_delivery', 'barcodes']]
        df.rename({
            'sku': 'артикул',
            'name': 'имя (необязательно)',
            'for_delivery': 'количество'
        }, axis='columns', inplace=True)

        file_path = dir_path / f'Склад {warehouse_name}, {datetime.now().strftime("%d.%m.%Y, %H:%M")}.xls'
        df.to_excel(file_path, index=False)


async def general_order_report(session: AsyncSession, dir_path: Path):
    rez = await db.get_general_order_data(session)
    df = pd.DataFrame(rez)
    df['total_cost_price'] = df['cost_price'] * df['for_delivery']
    df['total_volume'] = df['volume'] * df['for_delivery']
    df['total_weight'] = df['self_weight'] * df['for_delivery']
    df = df[['sku', 'name', 'for_delivery', 'self_weight', 'total_weight', 'volume', 'total_volume', 'cost_price', 'total_cost_price']]
    df.fillna(0, inplace=True)
    total_row = ['Итого', np.nan, np.nan, np.nan, df['total_weight'].sum(), np.nan, df['total_volume'].sum(), np.nan,
                 df['total_cost_price'].sum()]
    df.loc[-1] = total_row
    df.index = df.index + 1
    df = df.sort_index()

    df.rename({
        'total_cost_price': 'Себестоимость',
        'total_volume': 'Объем л',
        'total_weight': 'Вес кг',
        'sku': 'SKU',
        'name': 'Наименование',
        'for_delivery': 'Кол-во',
        'cost_price': 'Себестоимост(одного)',
        'self_weight': 'Вес(одного)',
        'volume': 'Объем(одного)'
    }, axis='columns', inplace=True)
    file_path = dir_path / f'Заказ, {datetime.now().strftime("%d.%m.%Y, %H:%M")}.xls'

    df.to_excel(file_path, index=False)


market_handlers = {
    'ozon': export_ozon_supply,
    'yandex': export_yandex_supply
}


@error_handler('Ошибка экспорта поставки.')
async def export_supply(name_of_shop: str | None = None, market: str | None = None):
    async with async_session() as session:
        rez = await db.get_supply_data(session, market, name_of_shop)

        if rez is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'No offers to supply')

        df = pd.DataFrame(rez)

        df['for_delivery'] = np.where(
            df['supplier_available'],
            df['for_delivery'],
            df[['for_delivery', 'own_storage_value']].min(axis=1)
        )

        # create zip archive/folder
        zip_file_path = Path(f'data/Поставка')
        zip_file_path.mkdir(parents=True, exist_ok=True)

        for _market in set(df['market'].values.tolist()):

            # create marketplace folder
            market_file_path = zip_file_path / _market
            market_file_path.mkdir(exist_ok=True)

            for _shop in set(df['name_of_shop'].values.tolist()):

                # create shop folder
                shop_file_path = market_file_path / _shop
                shop_file_path.mkdir(exist_ok=True)

                handler = market_handlers.get(_market, None)

                if handler is None:
                    raise KeyError(f'Market \'{_market}\' not found in registered')

                temp_df = df[(df['market'] == _market) & (df['name_of_shop'] == _shop)]

                # create supply files in directory
                await handler(temp_df, shop_file_path)

        await general_order_report(session, zip_file_path)

        # archive created directory
        response_file_path = make_archive(str(zip_file_path), root_dir=zip_file_path, format='zip')

        # remove files and dirs
        clean_up_files(str(zip_file_path))
        return response_file_path
