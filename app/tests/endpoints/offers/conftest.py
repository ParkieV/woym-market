import pytest

from src.api.factory import APITypes


def pricing_schemes():
    yandex_schemes = [
        ({
             'name': 'Y0',
             'market': APITypes.YANDEX,
             'fields': [
                 {
                     'key': 'cost_price',
                     'name': 'Себестоимость',
                     'pricing_scheme_name': 'Y0'
                 },
             ]
         }, True
        ),
        ({
             'name': 'Y1',
             'market': APITypes.YANDEX,
             'fields': [
                 {
                     'key': 'nothing',
                     'name': 'nothing',
                     'pricing_scheme_name': 'Y1'
                 },
             ]
         }, False
        )
    ]
    ozon_schemes = [
        ({
             'name': 'O0',
             'market': APITypes.OZON,
             'fields': [
                 {
                     'key': 'cost_price',
                     'name': 'Себестоимость',
                     'pricing_scheme_name': 'O0'
                 }
             ]
         }, True)
    ]
    return yandex_schemes + ozon_schemes
