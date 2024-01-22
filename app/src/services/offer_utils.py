import pandas as pd
import numpy as np
import json
from io import BytesIO


def count_fby(data: pd.DataFrame):
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

    data['fby'] = data['current_price'] * 0.2 + delivery_and_warehouse_processing_price
    return data['fby']


def calculate_offers_values(data: pd.DataFrame, course: float) -> pd.DataFrame:
    data['fby'] = count_fby(data)
    data['yandex_volume'] = data['yandex_length'] * data['yandex_width'] * data['yandex_height'] / 1000
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


def build_offers_data(data: pd.DataFrame, course: float = 5, total_price_coeff: float = 2.4, total_price_min_additional: float = 200, setup_mode: bool = False):
    if setup_mode:
        data['dollar_cost_price'] = 0  # закупка
    data['total_price_coeff'] = total_price_coeff
    data['total_price_min_additional'] = total_price_min_additional

    data['auto_min_price'] = 100
    data['manual_min_price'] = 100
    data['target_price'] = None

    data['use_manual_min_price'] = False
    data['auto_price_control'] = True

    data = calculate_offers_values(data, course)
    data['auto_price_control'] = False

    return json.loads(data.to_json(orient='records'))


def update_offers_data(data: pd.DataFrame, changes: pd.DataFrame, course: float):
    updated_offers: pd.DataFrame = data.copy()

    updated_offers.sort_values(['sku', 'name_of_shop'], inplace=True)
    updated_offers.reset_index(drop=True, inplace=True)

    changes.sort_values(['sku', 'name_of_shop'], inplace=True)
    changes.reset_index(drop=True, inplace=True)

    updated_offers.update(changes)
    updated_offers.drop('id', axis=1, errors='ignore')

    updated_offers = calculate_offers_values(updated_offers, course)

    return json.loads(updated_offers.to_json(orient='records'))


def bytes_to_data_frame(data: bytes) -> pd.DataFrame:
    io = BytesIO(data)
    return pd.read_excel(io, engine='openpyxl')
