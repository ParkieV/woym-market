
from src.api.exceptions import InitializationError
from src.api.interfaces import IApiGateway, IApiGatewayFactory, ApiTypes
from src.api.yandex import YandexMarketApi
from src.api.ozon import OzonApi
from src.api.wildberries import WildberriesApi


class ApiFactory(IApiGatewayFactory):
    api_types: dict[ApiTypes, type[IApiGateway]] = {
        ApiTypes.YANDEX: YandexMarketApi,
        ApiTypes.OZON: OzonApi,
        ApiTypes.WILDBERRIES: WildberriesApi
    }

    def __call__(self, api_type: ApiTypes, **attrs) -> IApiGateway:
        api_class = self.api_types.get(api_type, None)

        if api_class is None:
            raise InitializationError(str(api_type), f'API \"{api_type}\"  не найдено в зарегистрированных')

        try:
            api_instance = api_class(**attrs)
        except TypeError as err:
            raise InitializationError(str(api_type.value), str(err)[str(err).rfind('init__()')+9
                                                                    if str(err).rfind('init__()') != -1
                                                                    else 0:])
        return api_instance
