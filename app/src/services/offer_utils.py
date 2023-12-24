from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np
import json
from src.schemas.yandex_api_schemas import ExtendedYandexOfferInfo


def count_fby(data: pd.DataFrame) -> float:
    return 100


def calculate_offers_values(data: pd.DataFrame, course: float) -> pd.DataFrame:
    data['fby'] = count_fby(data)
    data['volume'] = (data['length'] * data['width'] * data['height']) / 100
    data['cost_price'] = data['parches'] * course
    data['settlement_price'] = np.where(data['cost_price'] > 200, data['cost_price'] * data['settlement_price_factor'],
                                        data['cost_price'] * data['settlement_price_factor'] + data['minimum_markup'])
    data['price_before_discount'] = data['settlement_price'] * 1.2
    data['profit'] = data['settlement_price'] - data['fby'] - data['cost_price']
    data['payback'] = data['cost_price'] * 100 / data['profit']
    return data


def build_offers_data(yandex_offers: list[ExtendedYandexOfferInfo], settlement_price_factor: float = 2.4,
                      minimum_markup: float = 200):
    course = 5
    data = pd.DataFrame(jsonable_encoder(yandex_offers))
    data['parches'] = np.random.randint(5, 100, size=(100, 1))  # закупка
    data['settlement_price_factor'] = settlement_price_factor
    data['minimum_markup'] = minimum_markup

    data = calculate_offers_values(data, course)

    return json.loads(data.to_json(orient='records'))


def update_offers_data(last_frame: pd.DataFrame, yandex_frame: pd.DataFrame):
    course = 5
    updated_data = last_frame.copy()
    for column_name in yandex_frame.columns:
        updated_data[column_name] = yandex_frame[column_name]

    updated_data = calculate_offers_values(updated_data, course)

    return json.loads(updated_data.to_json(orient='records'))


