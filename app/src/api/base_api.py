from abc import ABC, abstractmethod
from src.schemas.base_api_schemas import APIOffer, APIWarehouse


class BaseAPI(ABC):

    @abstractmethod
    async def check_auth_data(self, **kwargs):
        pass

    @abstractmethod
    async def get_offers_list(self) -> list[APIOffer]:
        pass

    @abstractmethod
    async def get_stocks(self) -> list[APIWarehouse]:
        pass

    @abstractmethod
    async def change_prices(self, *args, **kwargs) -> None:
        pass

