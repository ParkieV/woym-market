from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np
import json
from src.schemas.yandex_api_schemas import ExtendedYandexOfferInfo
from src.schemas.offer_schemas import OfferChange
from io import BytesIO


def count_fby(data: pd.DataFrame):
    dimensions_sum = data['length'] + data['width'] + data['height']
    data['fby'] = np.where(dimensions_sum < (150 / 100), data['current_price'] * 0.085, 850)
    return data['fby']


def calculate_offers_values(data: pd.DataFrame, course: float) -> pd.DataFrame:
    data['fby'] = count_fby(data)
    data['volume'] = data['length'] * data['width'] * data['height']
    data['cost_price'] = data['dollar_cost_price'] * course
    data['total_price'] = np.where(data['cost_price'] > data['total_price_min_additional'], data['cost_price'] * data['total_price_coeff'],
                                        data['cost_price'] * data['total_price_coeff'] + data['total_price_min_additional'])
    data['discount_base_price'] = data['total_price'] * 1.2
    data['profit'] = data['total_price'] - data['fby'] - data['cost_price']
    data['margin'] = data['cost_price'] * 100 / data['profit']

    return data


def calculate_yandex_price(data: pd.DataFrame) -> pd.DataFrame:
    data['current_price'] = np.where(
        data['auto_min_price'] & ~data['use_manual_min_price'],
        np.where(
            data['minimum_group_price'] > data['cost_price'],
            data['minimum_group_price'], data['cost_price']
        ), data['current_price'])

    return data


def build_offers_data(data: pd.DataFrame, course: float = 5,  total_price_coeff: float = 2.4,
                      total_price_min_additional: float = 200, setup_mode: bool = False):
    if setup_mode:
        data['dollar_cost_price'] = np.random.randint(5, 100, size=(data.shape[0], 1))  # закупка
    data['total_price_coeff'] = total_price_coeff
    data['total_price_min_additional'] = total_price_min_additional

    data['auto_min_price'] = False
    data['use_manual_min_price'] = False

    data = calculate_offers_values(data, course)

    return json.loads(data.to_json(orient='records'))


def update_offers_data(data: pd.DataFrame, changes: pd.DataFrame, course: float):
    updated_offers: pd.DataFrame = data.copy()

    updated_offers.sort_values('sku', inplace=True)
    updated_offers.reset_index(drop=True, inplace=True)

    changes.sort_values('sku', inplace=True)
    changes.reset_index(drop=True, inplace=True)

    updated_offers.update(changes)
    updated_offers.drop('id', axis=1)

    updated_offers = calculate_offers_values(updated_offers, course)

    return json.loads(updated_offers.to_json(orient='records'))


def bytes_to_data_frame(data: bytes) -> pd.DataFrame:
    io = BytesIO(data)
    return pd.read_excel(io, engine='openpyxl')

