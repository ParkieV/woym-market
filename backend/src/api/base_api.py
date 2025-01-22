from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from requests import Response
from src.schemas.base_api_schemas import APIOffer, APIWarehouse, APIPriceChangeData, APIOfferChangeData, APIOrderData

# Must be match to IApiGateway
class BaseAPI(ABC):
    market_type: str
    name_of_shop: str

    @abstractmethod
    async def validate_auth_data(self, **kwargs):
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
    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        raise NotImplementedError

    @abstractmethod
    async def request(self, method: str, url: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None,  headers: dict[str, Any] | None = None, include_response_logs: bool = False) -> Response:
        raise NotImplementedError
