import pandas as pd
import numpy as np
import json
from io import BytesIO
from fastapi import HTTPException, status


def count_fby(data: pd.DataFrame, settings) -> pd.Series:
    data = data.copy()
    # 19% - коммисия за продажу (дача, сад и огород, содовый инвентарь)
    # 1% - перевод денежных средств магазину
    # если dimensions_sum < 150 и вес < 25 кг, то 3% (20 <= x <= 60), иначе 350 - доставка внутри округа
    # если dimensions_sum < 150 и вес < 25 кг, то 3% (20 <= x <= 60), иначе 350 - доставка внутри округа

    dimensions_sum = data['yandex_length'] + data['yandex_width'] + data['yandex_height']
    delivery_and_warehouse_processing_price = np.where(
        (dimensions_sum < 150) | (data['yandex_weight'] < 25),
        data['current_price'] * 0.06,
        350 * 2
    )

    data['fby'] = data['current_price'] * (settings.fby_sales_commission / 100) + delivery_and_warehouse_processing_price + data['current_price'] * 0.01
    return data['fby']


def calculate_offers_values(data: pd.DataFrame, settings) -> pd.DataFrame:
    data = data.copy()

    data['fby'] = count_fby(data, settings)
    data['yandex_volume'] = data['yandex_length'] * data['yandex_width'] * data['yandex_height'] / 1000
    data['volume'] = data['self_length'] * data['self_width'] * data['self_height'] / 1000
    data['volume_difference'] = data['yandex_volume'] / data['volume']
    data['cost_price'] = data['dollar_cost_price'] * settings.rate
    data['total_price'] = np.where(data['cost_price'] > data['total_price_min_additional'],
                                   data['cost_price'] * data['total_price_coeff'],
                                   data['cost_price'] * data['total_price_coeff'] + data['total_price_min_additional'])

    data = calculate_price(data)

    data['profit'] = data['current_price'] - data['fby'] - data['cost_price']
    data['margin'] = data['cost_price'] * 100 / data['profit']
    data['discount_base_price'] = data['current_price'] * 1.2

    return data


def calculate_price(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    # не меняем цену
    # sub_data_1 = data[data['auto_price_control'] == False]
    # sub_data_1.loc[:, 'target_price'] = sub_data_1['target_price']


    # используем ручную мин планку
    sub_data_2 = data[data['use_manual_min_price'] == True]
    sub_data_2.loc[:, 'target_price'] = np.where(
        sub_data_2['current_price'] >= sub_data_2['best_price_im'],
        sub_data_2[['best_price_im', 'manual_min_price']].max(axis=1),
        sub_data_2[['total_price', 'best_price_im']].min(axis=1)
    )

    #  используем автоматическую мин планку
    sub_data_3 = data[data['use_manual_min_price'] == False]
    sub_data_3['temp_auto_min_price'] = sub_data_3['total_price'] * sub_data_3['auto_min_price'] / 100
    sub_data_3.loc[:, 'target_price'] = np.where(
        sub_data_3['current_price'] >= sub_data_3['best_price_im'],
        sub_data_3[['best_price_im', 'temp_auto_min_price']].max(axis=1),
        sub_data_3[['total_price', 'best_price_im']].min(axis=1)
    )
    sub_data_3.drop('temp_auto_min_price', axis=1, inplace=True)

    df = pd.concat([sub_data_2, sub_data_3])
    df.reset_index(drop=True, inplace=True)

    # прибовляем 5% если магазин с лучшей ценой это текущий магазин
    df['target_price'] = np.where(
        (df['best_place_im'] == df['name_of_shop']) & (df['best_price_im'] == df['target_price']),
        df['target_price'] * 1.05,
        df['target_price']
    )
    return df


def build_offers_data(data: pd.DataFrame, settings, total_price_coeff: float = 2.4, total_price_min_additional: float = 200, setup_mode: bool = False) -> pd.DataFrame:
    data = data.copy()

    if setup_mode:
        data['dollar_cost_price'] = np.nan  # закупка
        data[['self_weight', 'self_length', 'self_width', 'self_height']] = np.nan

    data['total_price_coeff'] = total_price_coeff
    data['total_price_min_additional'] = total_price_min_additional

    data['auto_min_price'] = 100
    data['manual_min_price'] = 100
    data['target_price'] = np.nan

    data['use_manual_min_price'] = False
    data['auto_price_control'] = True

    data = calculate_offers_values(data, settings)
    data['auto_price_control'] = False

    return data


def update_offers_data(data: pd.DataFrame, changes: pd.DataFrame, settings) -> pd.DataFrame:
    updated_offers: pd.DataFrame = data.copy()

    updated_offers.sort_values(['sku', 'name_of_shop'], inplace=True)
    updated_offers.reset_index(drop=True, inplace=True)

    changes.sort_values(['sku', 'name_of_shop'], inplace=True)
    changes.reset_index(drop=True, inplace=True)

    updated_offers.update(changes)
    updated_offers.drop('id', axis=1, errors='ignore')

    updated_offers = calculate_offers_values(updated_offers, settings)
    updated_offers[['note_1', 'note_2', 'note_3']].fillna('', inplace=True)
    updated_offers['hidden'].fillna(False, inplace=True)

    return updated_offers


def bytes_to_data_frame(data: bytes, sheet_name: str | int = 0, file_extension: str = 'xlsx') -> pd.DataFrame:
    io = BytesIO(data)
    pd_engine = {
        '.xlsx': 'openpyxl',
        '.xls': 'xlrd'
    }
    if file_extension not in pd_engine.keys():
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f'File extension "{file_extension}" not supported')

    return pd.read_excel(io, engine=pd_engine[file_extension], sheet_name=sheet_name)
