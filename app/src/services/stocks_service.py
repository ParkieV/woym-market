from itertools import chain
from typing import Callable
import numpy as np
import pandas as pd
from fastapi import HTTPException
from starlette import status
import openpyxl
import src.services.base_utils
from logs import get_logger
from src.api.wrapper import APIWrapper
from src.database.db import async_session
from src.database import warehouse_db as db
from src.database.models.models import Offer
from src.database.offer_db import get_offers_fields
from src.params.confing import config
from src.schemas.filters.stocks_filter import WarehousesFilter
from src.schemas.offer_schemas import OfferOut
from src.schemas.stocks.own_storages_schemas import OwnStorageUpdate, OwnStoragePlaceCreate, \
    OwnStoragePlaceOut, OwnStoragePlaceUpdate
from src.schemas.stocks.fbo_schemas import OfferFBOStockUpdate, OfferStockOut, AggOfferFBOStock
from src.schemas.stocks.stocks_schemas import SupplyExportType, GeneralOrderData
from src.schemas.stocks.warehouses_schemas import WarehouseCreate, WarehouseOut
from src.services.base_utils import error_handler, clean_up_files, validate_dataframe
from datetime import datetime
from pathlib import Path
from shutil import make_archive

api_wrapper = APIWrapper()

logger = get_logger(__name__)


async def update_warehouses_and_stocks():
    logger.info('Start update warehouses and stocks')

    start_time = datetime.now()

    async with async_session() as session:
        # Остатки из API
        stocks = await api_wrapper.get_stocks()
        logger.info('API stocks collected')

        api_stocks_df = pd.DataFrame([{
            'warehouse_name': warehouse.name,
            'warehouse_type': warehouse.warehouse_type,
            'market': warehouse.market,
            'sku': [stock.sku for stock in warehouse.offers],
            'name_of_shop': [stock.name_of_shop for stock in warehouse.offers],
            'current_stock': [stock.current_stock for stock in warehouse.offers],
        } for warehouse in stocks])
        api_stocks_df_exploded = api_stocks_df.explode(['sku', 'name_of_shop', 'current_stock'])
        api_stocks_df_exploded.dropna(inplace=True)
        api_stocks_df_exploded[['sku', 'name_of_shop', 'market', 'warehouse_name']] = api_stocks_df_exploded[
            ['sku', 'name_of_shop', 'market', 'warehouse_name']].astype('string')

        # Остатки из БД
        db_stocks = await db.get_all_offers_stocks(session)
        db_stocks_df = pd.DataFrame(db_stocks, columns=['id', 'current_stock', 'offer_id', 'warehouse_name', 'sku', 'market', 'name_of_shop'])

        # Создание новых складов
        for warehouse in stocks:
            await db.update_or_create_warehouse(session, WarehouseCreate(
                market=warehouse.market,
                name=warehouse.name,
                warehouse_type=warehouse.warehouse_type,
            ))
        logger.info('Warehouses created')

        # Обновение остатков, у которых current_stock не совпадает с уже установленными
        merged_stocks = pd.merge(api_stocks_df_exploded, db_stocks_df, how='outer', on=('sku', 'name_of_shop', 'market', 'warehouse_name'), indicator=True, suffixes=(None, '__db'))
        to_update_df = merged_stocks[merged_stocks['_merge'] == 'both']
        to_update_df = to_update_df[to_update_df['current_stock'] != to_update_df['current_stock__db']][['id', 'current_stock']]
        await db.update_fbo_stocks(session, to_update_df.to_dict('records'))
        logger.info(f'FBO stocks updated: {len(to_update_df)}')

        # Создание новых остатков
        to_create_df = merged_stocks[merged_stocks['_merge'] == 'left_only'].drop(columns=['offer_id', 'id', '_merge'])
        offers_idents = await get_offers_fields(session, [Offer.id, Offer.sku, Offer.name_of_shop, Offer.market])
        offers_idents_df = pd.DataFrame(offers_idents, columns=['offer_id', 'sku', 'name_of_shop', 'market'])
        warehouses_df = pd.DataFrame([i.model_dump() for i in await db.get_warehouses(session)]).rename(columns={'name': 'warehouse_name', 'id': 'warehouse_id'})
        to_create_df = pd.merge(to_create_df, offers_idents_df, how='inner', on=['sku', 'market', 'name_of_shop'])
        to_create_df = pd.merge(to_create_df, warehouses_df, how='inner', on=['warehouse_name', 'market', 'warehouse_type'])
        to_create_df = to_create_df[['offer_id', 'current_stock', 'warehouse_id']]

        # Создание новых остатков
        await db.create_fbo_stocks_(session, to_create_df.to_dict('records'))
        logger.info(f'New fbo stocks created: {len(to_create_df)}')

        # Создать остатки на складах, которые не были в полученных данных
        await db.fill_empty_stocks(session)
        logger.info('Empty fbo stocks filled')

        await db.relate_warehouses_with_clusters(session,
                                                 [{'name': i.name, 'related_warehouses_name': i.related_warehouses_name}
                                                  for i in stocks])
        logger.info('Related warehouses relation filled')
        # await db.recalculate_clusters(session)
        # await db.recalculate_stocks_for_delivery(session)
        await db.recalculate_stocks_for_delivery(session)
        logger.info('Recalculate stocks and clusters for delivery')

    end_time = datetime.now()

    logger.info(f'Update warehouses and stocks completed in {end_time - start_time}')


# async def update_or_create_super_clusters():


async def get_warehouses(filter: WarehousesFilter | None = None):
    async with async_session() as session:
        return await db.get_warehouses(session, filter_=filter)


@error_handler('Не удалось получить собственные остатки.')
async def get_own_storages():
    async with async_session() as session:
        return await db.get_own_storages(session)


@error_handler('Не удалось обновить собственные остатки.')
async def change_own_storages(data: list[OwnStorageUpdate]):
    async with async_session() as session:
        await db.change_own_storages(session, data)


@error_handler('Ошибка экспорта собственных остатков.')
async def export_own_storages(place_id: int) -> str:
    async with async_session() as session:
        data = await db.get_own_storages(session, place_id)
        storage_place = await db.get_own_storage_place(session, place_id)

    offers_data = [{
        'sku': i.offer.sku,
        'name': ', '.join(i.offer.name),
        'photo': ', '.join([j for j in i.offer.photo if j is not None]),
        'market': ', '.join(i.offer.market),
        'name_of_shop': ', '.join(i.offer.name_of_shop),
        'note_1': ', '.join([j for j in i.offer.note_1 if j is not None]),
        'note_2': ', '.join([j for j in i.offer.note_2 if j is not None]),
        'note_3': ', '.join([j for j in i.offer.note_3 if j is not None]),
        'barcodes': ', '.join([j for j in i.offer.barcodes if j is not None]),

    } for i in data]
    offers_df = pd.DataFrame(offers_data)
    offers_df['sku'] = offers_df['sku'].astype('string')

    stocks_data = chain.from_iterable(
        [[{'sku': i.offer.sku, f'{stock.name_of_shop} ({stock.market})': stock.stock} for stock in i.stocks] for i in
         data])
    stocks_df = pd.DataFrame(stocks_data)
    stocks_df['sku'] = stocks_df['sku'].astype('string')
    stocks_df = stocks_df.groupby('sku', as_index=False).sum()

    own_storage_data = chain.from_iterable([[{'sku': storage.sku,
                                              f'Мой склад': storage.value}
                                             for storage in i.storages] for i in data])
    own_storages_df = pd.DataFrame(own_storage_data)
    own_storages_df['sku'] = own_storages_df['sku'].astype('string')

    offers_with_stocks_df = offers_df.merge(stocks_df, on='sku', how='outer')
    df = offers_with_stocks_df.merge(own_storages_df, on='sku', how='outer')
    df.rename({
        'name': 'Название',
        'photo': 'Фото',
        'market': 'Маркетплейс',
        'name_of_shop': 'Название магазина',
        'barcodes': 'Коды',
        'note_1': 'Примечание 1',
        'note_2': 'Примечание 2',
        'note_3': 'Примечание 3',
    }, axis='columns', inplace=True)
    df.to_excel(f'data/Мой склад {storage_place.name}.xlsx', index=False)
    return f'data/Мой склад {storage_place.name}.xlsx'


@error_handler('Ошибка импорта собственных остатков.')
async def import_own_storages(data, place_id: int, file_extension: str = 'xlsx'):
    df = src.services.base_utils.bytes_to_data_frame(data, file_extension=file_extension)
    df.rename(columns=OfferOut.reverse_fields(), inplace=True)
    df.rename(columns={'Мой склад': 'value'}, inplace=True)
    df = df[['sku', 'value']]
    df = df.astype({'sku': str, 'value': int})
    data = df.to_dict('records')

    async with async_session() as session:
        await db.update_own_storages_by_sku(session, data, place_id)


async def export_yandex_supply(data: pd.DataFrame, dir_path: Path):
    warehouses = set(data['warehouse_name'].values.tolist())

    for warehouse_name in warehouses:
        df = data[data['warehouse_name'] == warehouse_name]
        df = df[['sku', 'name', 'barcodes', 'for_delivery', 'current_price']]
        df.rename({
            'sku': 'Ваш SKU',
            'name': 'Название товара',
            'for_delivery': 'Количество товаров в поставке',
            'current_price': 'Объявленная ценность одного товара, руб.',
            'barcodes': 'Штрихкоды'
        }, axis='columns', inplace=True)
        df['НДС'] = 'VAT_20'
        file_path = dir_path / f'Склад {warehouse_name.replace("/", "|")}, {datetime.now(tz=config.time_zone_ino).strftime("%d.%m.%Y, %H:%M")}.xlsx'
        df.to_excel(file_path, index=False, header=True, sheet_name='Поставка', startrow=1)

        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
        ws.cell(1, 1, value='Данные для поставки')
        wb.save(file_path)


async def export_ozon_supply(data: pd.DataFrame, dir_path: Path):
    warehouses = set(data['warehouse_name'].values.tolist())

    for warehouse_name in warehouses:
        df = data[data['warehouse_name'] == warehouse_name]
        df = df[['sku', 'name', 'for_delivery']]
        df.rename({
            'sku': 'артикул',
            'name': 'имя (необязательно)',
            'for_delivery': 'количество'
        }, axis='columns', inplace=True)

        file_path = dir_path / f'Склад {warehouse_name.replace("/", "-")}, {datetime.now(tz=config.time_zone_ino).strftime("%d.%m.%Y, %H:%M")}.xlsx'
        df.to_excel(file_path, index=False)


async def export_wildberries_supply(data: pd.DataFrame, dir_path: Path):
    warehouses = set(data['warehouse_name'].values.tolist())

    for warehouse_name in warehouses:
        df = data[data['warehouse_name'] == warehouse_name]
        df = df[['barcodes', 'for_delivery', 'sku']]

        df['barcodes'] = df['barcodes'].apply(lambda x: x.split(', ')[0] if x else np.nan)
        df.dropna(axis='rows', inplace=True)

        df.rename({
            'sku': 'Артикул поставщика',
            'for_delivery': 'Количество, шт.',
            'barcodes': 'Баркод'
        }, axis='columns', inplace=True)

        file_path = dir_path / f'Склад {warehouse_name.replace("/", "-")}, {datetime.now(tz=config.time_zone_ino).strftime("%d.%m.%Y, %H:%M")}.xlsx'
        df.to_excel(file_path, index=False)


async def general_order_report(
        data: list[GeneralOrderData],
        dir_path: Path,
        file_type_name: str = 'Заказ',
        fd_builder_func: Callable[[pd.DataFrame], pd.Series] | None = None
):
    df = pd.DataFrame([i.model_dump() for i in data])

    if fd_builder_func:
        df['for_delivery'] = fd_builder_func(df)

    df['total_cost_price'] = df['cost_price'] * df['for_delivery']
    df['total_volume'] = df['volume'] * df['for_delivery']
    df['total_weight'] = df['self_weight'] * df['for_delivery']
    df = df[['sku', 'name', 'for_delivery', 'self_weight', 'total_weight', 'volume', 'total_volume', 'cost_price',
             'total_cost_price']]
    df.fillna(0, inplace=True)
    df = df[df['for_delivery'] > 0]

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

    file_path = dir_path / f'{file_type_name}, {datetime.now(tz=config.time_zone_ino).strftime("%d.%m.%Y, %H:%M")}.xlsx'
    df.to_excel(file_path, index=False)


market_handlers = {
    'ozon': export_ozon_supply,
    'yandex': export_yandex_supply,
    'wildberries': export_wildberries_supply
}


@error_handler('Ошибка экспорта поставки.')
async def export_supply(export_type: SupplyExportType, warehouses: list[int], offers: list[int],
                        place_id: int | None = None):
    if not warehouses:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для формирования поставки нужно указать склады')

    if not offers:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для формирования поставки нужно передать товары')

    async with async_session() as session:
        if export_type == SupplyExportType.ONLY_OWN_STORAGE:
            offers_data, aggregated_offers_data = await db.get_supply_only_own_storage(session=session,
                                                                                       warehouses=warehouses,
                                                                                       offers=offers, place_id=place_id)
            df = pd.DataFrame([i.model_dump() for i in offers_data])

        elif export_type == SupplyExportType.WITH_OWN_STORAGE:
            offers_data, aggregated_offers_data = await db.get_supply_only_own_storage(session=session,
                                                                                       warehouses=warehouses,
                                                                                       offers=offers, place_id=place_id)
            df = pd.DataFrame([i.model_dump() for i in offers_data])
            df['for_delivery'] = df['base_for_delivery']
        else:
            offers_data, aggregated_offers_data = await db.get_supply_only_stocks(session=session,
                                                                                  warehouses=warehouses, offers=offers,
                                                                                  place_id=place_id)
            df = pd.DataFrame([i.model_dump() for i in offers_data])

        if not all((offers_data, aggregated_offers_data)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Данных для поставки не найдено')

        df = df[df['for_delivery'] > 0]

        if not len(df):
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Товаров с ненулевым значением "к поставке" не найдено')

        # create zip archive/folder
        zip_file_path = Path(f'data/Поставка')
        zip_file_path.mkdir(parents=True, exist_ok=True)

        for _market in set(df['market'].values.tolist()):

            # create marketplace folder
            market_file_path = zip_file_path / _market
            market_file_path.mkdir(exist_ok=True)
            for _shop in set(df[df['market'] == _market]['name_of_shop'].values.tolist()):

                # create shop folder
                shop_file_path = market_file_path / _shop
                shop_file_path.mkdir(exist_ok=True)

                handler = market_handlers.get(_market, None)

                if handler is None:
                    raise KeyError(f'Market \'{_market}\' not found in registered')

                temp_df = df[(df['market'] == _market) & (df['name_of_shop'] == _shop)]

                # create supply files in directory
                await handler(temp_df, shop_file_path)

        if export_type == SupplyExportType.WITH_OWN_STORAGE:
            await general_order_report(aggregated_offers_data, zip_file_path, file_type_name='Заказ (в наличии)',
                                       fd_builder_func=lambda x: x['for_delivery'])
            await general_order_report(aggregated_offers_data, zip_file_path, file_type_name='Заказ (дозаказать)',
                                       fd_builder_func=lambda x: x['base_for_delivery'] - x['for_delivery'])
        else:
            await general_order_report(aggregated_offers_data, zip_file_path)

        # archive created directory
        response_file_path = make_archive(str(zip_file_path), root_dir=zip_file_path, format='zip')

        # remove files and dirs
        clean_up_files(str(zip_file_path))
        return response_file_path


async def import_fbo_data(data, name_of_shop: str | None, warehouse_id: int | None, file_extension: str) -> str:
    df = src.services.base_utils.bytes_to_data_frame(data, file_extension=file_extension, header=1)
    df.rename({
        'Ваш SKU': 'sku',
        'Можно ли поставить товар?': 'can_be_delivered',
        'Совет': 'advice_from_the_store'
    }, inplace=True, axis='columns')
    df = df[['sku', 'can_be_delivered', 'advice_from_the_store']]
    df['can_be_delivered'] = df['can_be_delivered'].replace({'да': True, 'нет': False})

    async with async_session() as session:
        await db.update_fbo_support_data(session, df.to_dict('records'), name_of_shop, warehouse_id)


async def get_warehouse(warehouse_id: int) -> WarehouseOut | None:
    async with async_session() as session:
        return await db.get_warehouse(session, warehouse_id)


async def create_own_storage_places(data: list[OwnStoragePlaceCreate]):
    async with async_session() as session:
        await db.create_own_storage_places(session, data)


async def get_all_own_storage_places() -> list[OwnStoragePlaceOut]:
    async with async_session() as session:
        return await db.get_all_own_storage_places(session)


async def change_own_storage_places(data: list[OwnStoragePlaceUpdate]):
    async with async_session() as session:
        await db.change_own_storage_places(session, data)


async def increment_own_storage_values(data, place_id: int, file_extension: str, coef: int = 1):
    df = src.services.base_utils.bytes_to_data_frame(data, file_extension=file_extension)

    if any(df.columns.str.contains('unnamed', case=False)):
        df.columns = df.iloc[0]
        df.drop(df.index[0], inplace=True)

    df.rename(columns={
        'артикул': 'sku',
        'количество': 'value',
        'Ваш SKU': 'sku',
        'Количество товаров в поставке': 'value',
        'SKU': 'sku',
        'Кол-во': 'value'
    }, inplace=True)

    df = validate_dataframe(df, required_columns=['sku', 'value'], full_entry=False, allow_change=True)

    df.dropna(axis='rows', inplace=True)
    df = df.astype({'sku': str, 'value': int})
    df['value'] = df['value'] * coef

    async with async_session() as session:
        await db.increment_own_storage_values(session, df.to_dict('records'), place_id)


async def get_offer_fbo_stocks(offer_id: int) -> list[OfferStockOut]:
    async with async_session() as session:
        return await db.get_offer_fbo_stocks(session, offer_id)


async def change_fbo_stocks(data: list[OfferFBOStockUpdate]):
    async with async_session() as session:
        await db.change_fbo_stocks(session, data)


async def aggregate_offers_fbo_stocks(warehouse_ids: list[int] | None = None, ignore_clusters: bool = True) -> list[AggOfferFBOStock]:
    async with async_session() as session:
        return await db.get_agg_fbo_data(session, warehouse_ids, ignore_clusters)
