from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np
import json
from src.schemas.yandex_api_schemas import ExtendedYandexOfferInfo
from src.schemas.offer_schemas import OfferChange
from io import BytesIO


def count_fby(data: pd.DataFrame) -> float:
    return 100


def calculate_offers_values(data: pd.DataFrame, course: float) -> pd.DataFrame:
    data['fby'] = count_fby(data)
    data['volume'] = data['length'] * data['width'] * data['height']
    data['cost_price'] = data['parches'] * course
    data['settlement_price'] = np.where(data['cost_price'] > 200, data['cost_price'] * data['settlement_price_factor'],
                                        data['cost_price'] * data['settlement_price_factor'] + data['minimum_markup'])
    data['price_before_discount'] = data['settlement_price'] * 1.2
    data['profit'] = data['settlement_price'] - data['fby'] - data['cost_price']
    data['payback'] = data['cost_price'] * 100 / data['profit']

    return data


def calculate_yandex_price(data: pd.DataFrame) -> pd.DataFrame:
    data['market_price'] = np.where(
        data['automatic_price_management'],
        np.where(
            data['minimum_group_price'] > data['cost_price'],
            data['minimum_group_price'], data['cost_price']
        ), None)

    return data


def build_offers_data(data: pd.DataFrame, course: float = 5,  settlement_price_factor: float = 2.4,
                      minimum_markup: float = 200, auto_min_price: bool = True, setup_mode: bool = False):
    if setup_mode:
        data['parches'] = np.random.randint(5, 100, size=(data.shape[0], 1))  # закупка
    data['settlement_price_factor'] = settlement_price_factor
    data['minimum_markup'] = minimum_markup

    data['automatic_price_management'] = auto_min_price
    data['manual_control_min_price'] = not auto_min_price

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

