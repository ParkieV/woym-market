import logging
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from aiohttp import ClientSession, ClientResponse

from logs import get_logger
from src.api.exceptions import RequestException
from src.api.interfaces import IApiGateway
from src.schemas.base_api_schemas import APIOfferChangeData, APIOffer, APIWarehouse, APIPriceChangeData, APIOrderData

api_logger = get_logger('API', level=logging.INFO)


@asynccontextmanager
async def get_api_session() -> AsyncGenerator[ClientSession, None]:
    async with ClientSession() as session:
        try:
            yield session
        except RequestException as exc:
            api_logger.error(exc)
            raise exc


class ApiGateway(IApiGateway):
    market_type: str
    name_of_shop: str
    session: ClientSession

    def __init__(self, token: str, entity_id: str | None, shop_name: str, session: ClientSession) -> None: #type: ignore
        self.name_of_shop = shop_name
        self.token = token
        self.shop_name = shop_name
        self.client_id = entity_id
        self.auth_headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.token,
        }
        self.session = session

    async def request(self, method: str, url: str, body: Sequence[dict] | dict | None = None, params: dict | None = None,  headers: dict | None = None, include_response_logs: bool = False) -> ClientResponse:
        """
        Отправка запроса по сети.
        :param method: Метод HTTP запроса.
        :param url: URL ссылка эндпоинта.
        :param body: Тело запроса.
        :param params: Query-параметры запроса.
        :param headers: Загаловки запроса.
        :param include_response_logs: Активировать логи запроса.
        :return: Ответ запроса.
        """
        response_log_message = (f'Request to API {self.market_type}({self.name_of_shop}): {method.upper()} {url} '
                                f''
                                f'| params={params} | headers={headers}.')

        try:
            response = await self.session.request(method=method, url=url, headers=headers, json=body, params=params)
        except Exception as e:
            api_logger.fatal(f'[FATAL] {response_log_message}', exc_info=e)
            raise RequestException(response_log_message)
        else:
            response_status = 'OK' if response.ok else 'FAILED'
            response_data = response.text if include_response_logs else '!transmission disabled'
            if api_logger.level == logging.DEBUG:
                api_logger.debug(f'[{response_status}] {response_log_message} Response from API: status={response.status} | content={response_data}')
            else:
                api_logger.info(f'[{response_status}] {response_log_message} Response from API: status={response.status}')

            return response

    async def _download_report(self, url_path: str) -> pd.DataFrame:
        output = BytesIO()
        response = await self.request('GET', url=url_path)
        output.write(await response.read())
        return pd.read_excel(output, engine='openpyxl')

    async def validate_response(self, response: ClientResponse, body: Any = None) -> Any:
        data_json = await response.json()

        if response.status != 200:
            raise RequestException(f'status: {response.status} \ndetail: {data_json}')

        return data_json

    async def validate_auth_data(self) -> None:
        ...

    async def change_offers(self, data: list[APIOfferChangeData]) -> None:
        ...

    async def get_offers_list(self) -> list[APIOffer]:
        ...

    async def get_stocks(self) -> list[APIWarehouse]:
        ...

    async def change_prices(self, data: list[APIPriceChangeData]) -> None:
        ...

    async def get_orders(self, from_date: datetime, to_date: datetime) -> list[APIOrderData]:
        ...
