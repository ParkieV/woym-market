from abc import ABC, abstractmethod
from io import BytesIO

import pandas as pd

from src.schemas.base_api_schemas import APIOffer, APIWarehouse, APIPriceChangeData


class BaseAPI(ABC):

    @abstractmethod
    async def validate_auth_data(self, **kwargs):
        pass

    @abstractmethod
    async def get_offers_list(self) -> list[APIOffer]:
        pass

    @abstractmethod
    async def get_stocks(self) -> list[APIWarehouse]:
        pass

    @abstractmethod
    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        pass

    def _download_report(self, url_path: str) -> pd.DataFrame:
        output = BytesIO()
        response = self.session.get(url_path)
        output.write(response.content)
        return pd.read_excel(output, engine='openpyxl')


