from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np
import json
from src.schemas.yandex_api_schemas import ExtendedYandexOfferInfo


def build_offers_data(yandex_offers: list[ExtendedYandexOfferInfo]):
    course = 5
    FBY = 100
    data = pd.DataFrame(jsonable_encoder(yandex_offers))
    data['parches'] = np.random.randint(5, 100, size=(100, 1))
    data['settlement_price_factor'] = np.random.randint(1, 5, size=(100, 1))
    data['volume'] = (data['length'] * data['width'] * data['height']) / 100
    data['cost_price'] = data['parches'] * course
    data['settlement_price_factor'] = 2.4
    data['minimum_markup'] = 200
    data['settlement_price'] = np.where(data['cost_price'] > 200, data['cost_price'] * data['settlement_price_factor'],
                                        data['cost_price'] * data['settlement_price_factor'] + data['minimum_markup'])
    data['price_before_discount'] = data['settlement_price'] * 1.2
    data['profit'] = data['settlement_price'] - FBY - data['cost_price']
    data['payback'] = data['cost_price'] * 100 / data['profit']
    return json.loads(data.to_json(orient='records'))

