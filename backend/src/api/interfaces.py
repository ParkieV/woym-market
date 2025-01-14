from abc import abstractmethod
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Protocol, Any, AsyncContextManager

from aiohttp import ClientSession, ClientResponse

from src.schemas.base_api_schemas import APIOfferChangeData, APIWarehouse, APIOffer, APIPriceChangeData, APIOrderData


IApiSessionFabric = Callable[[], AsyncContextManager[ClientSession]]


class ApiTypes(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yandex'
    WILDBERRIES = 'wildberries'


class IApiGateway(Protocol):
    market_type: str
    name_of_shop: str
    session: ClientSession

    @abstractmethod
    def __init__(self, token: str, entity_id: int | None, shop_name: str, session: ClientSession) -> None:
        raise NotImplementedError

    @abstractmethod
    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_offers_list(self) -> list[APIOffer]:
        raise NotImplementedError

    @abstractmethod
    async def get_stocks(self) -> list[APIWarehouse]:
        raise NotImplementedError

    @abstractmethod
    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        raise NotImplementedError

    @abstractmethod
    async def request(self, method: str, url: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None,  headers: dict[str, Any] | None = None, include_response_logs: bool = False) -> ClientResponse:
        raise NotImplementedError

    @abstractmethod
    async def validate_response(self, response: ClientResponse, body: Any = None) -> Any:
        raise NotImplementedError

class IApiGatewayFactory(Protocol):
    api_types: dict[ApiTypes, type[IApiGateway]]

    @abstractmethod
    def __call__(self, api_type: ApiTypes) -> IApiGateway:
        raise NotImplementedError
