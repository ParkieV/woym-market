from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np
import json
from io import BytesIO


def count_fby(data: pd.DataFrame):
    dimensions_sum = data['length'] + data['width'] + data['height']
    data['fby'] = np.where(dimensions_sum < (150 / 100), data['current_price'] * 0.085, 850)
    return data['fby']


def calculate_offers_values(data: pd.DataFrame, course: float) -> pd.DataFrame:
    data['fby'] = count_fby(data)
    data['volume'] = data['length'] * data['width'] * data['height'] * 100 * 1000
    data['cost_price'] = data['dollar_cost_price'] * course
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
    sub_data_1 = data[data['auto_price_control'] == False]
    sub_data_1.loc[:, 'target_price'] = sub_data_1['target_price']


    # используем ручную мин планку
    sub_data_2 = data[((data['auto_price_control'] == True) & (data['use_manual_min_price'] == True))]
    sub_data_2.loc[:, 'target_price'] = np.where(
        sub_data_2['current_price'] >= sub_data_2['minimum_group_price'],
        sub_data_2[['minimum_group_price', 'manual_min_price']].max(axis=1),
        sub_data_2[['total_price', 'minimum_group_price']].min(axis=1)
    )

    #  используем автоматическую мин планку
    sub_data_3 = data[((data['auto_price_control'] == True) & (data['use_manual_min_price'] == False))]
    sub_data_3['temp_auto_min_price'] = sub_data_3['total_price'] * sub_data_3['auto_min_price'] / 100
    sub_data_3.loc[:, 'target_price'] = np.where(
        sub_data_3['current_price'] >= sub_data_3['minimum_group_price'],
        sub_data_3[['minimum_group_price', 'temp_auto_min_price']].max(axis=1),
        sub_data_3[['total_price', 'minimum_group_price']].min(axis=1)
    )
    sub_data_3.drop('temp_auto_min_price', axis=1, inplace=True)

    df = pd.concat([sub_data_1, sub_data_2, sub_data_3])
    df.reset_index(drop=True, inplace=True)

    # прибовляем 5% если магазин с лучшей ценой это текущий магазин
    df['target_price'] = np.where(
        (df['auto_price_control'] == True) & (df['minimum_group_price_shop'] == df['name_of_shop']) & (df['minimum_group_price'] == df['target_price']),
        df['target_price'] * 1.05,
        df['target_price']
    )
    return df


def build_offers_data(data: pd.DataFrame, course: float = 5, total_price_coeff: float = 2.4, total_price_min_additional: float = 200, setup_mode: bool = False):
    if setup_mode:
        data['dollar_cost_price'] = 0  # закупка
    data['total_price_coeff'] = total_price_coeff
    data['total_price_min_additional'] = total_price_min_additional

    data['use_manual_min_price'] = True
    data['auto_min_price'] = 110
    data['manual_min_price'] = None
    data['auto_price_control'] = False
    data['target_price'] = None

    data = calculate_offers_values(data, course)

    return json.loads(data.to_json(orient='records'))


def update_offers_data(data: pd.DataFrame, changes: pd.DataFrame, course: float):
    updated_offers: pd.DataFrame = data.copy()

    updated_offers.sort_values('sku', inplace=True)
    updated_offers.reset_index(drop=True, inplace=True)

    changes.sort_values('sku', inplace=True)
    changes.reset_index(drop=True, inplace=True)

    updated_offers.update(changes)
    updated_offers.drop('id', axis=1, errors='ignore')

    updated_offers = calculate_offers_values(updated_offers, course)

    return json.loads(updated_offers.to_json(orient='records'))


def bytes_to_data_frame(data: bytes) -> pd.DataFrame:
    io = BytesIO(data)
    return pd.read_excel(io, engine='openpyxl')
