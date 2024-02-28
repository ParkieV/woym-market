from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import HTTPException
from requests import Response

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

    def _raise_error(self, detail: str, status_code: int = 500, body: Any = None):
        # TODO write logs
        raise HTTPException(status_code, detail, body)

    def validate_response(self, response: Response, raise_error: bool = True, body: Any = None) -> Any:
        if response.status_code != 200:
            if raise_error:
                self._raise_error(response.json(), response.status_code, body)
            else:
                print(response.reason, response.status_code, response.json(), body)
        return response.json()


