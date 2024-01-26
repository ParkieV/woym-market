from typing import TypeVar, Callable
from collections import defaultdict

StocksResponseHandler = Callable[[list[dict]], defaultdict]


def OFFERS_DETAIL(warehouses: list[dict]):
    result = defaultdict(list)

    for warehouse in warehouses:
        for offer in warehouse['offers']:
            result[offer['offerId']].extend(offer['stocks'])

    return result


def OFFERS(warehouses: list[dict]):
    """Returns [{
        offerId: int
    }]"""

    result = defaultdict(int)

    for warehouse in warehouses:
        for offer in warehouse['offers']:
            result[offer['offerId']] += sum([i['count'] for i in offer['stocks'] if i['type'] == 'AVAILABLE'])

    return result


def WAREHOUSES(warehouses: list[dict]) -> defaultdict[int, list[dict]]:
    result = defaultdict(list)
    for warehouse in warehouses:
        result[warehouse['warehouseId']].extend(warehouse['offers'])

    return result
