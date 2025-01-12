from src.api.interfaces import ApiTypes


def pricing_schemes():
    yandex_schemes = [
        ({
             'name': 'Y0',
             'market': ApiTypes.YANDEX,
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
             'market': ApiTypes.YANDEX,
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
             'market': ApiTypes.OZON,
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
