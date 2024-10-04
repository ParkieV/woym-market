import logging
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from logs import get_logger

logger = get_logger('endpoints', level=logging.DEBUG)


class EndpointLoggingMiddleware(BaseHTTPMiddleware):
    # def __init__(self, app, *args, **kwargs):
    #     super().__init__(app, *args, **kwargs)

    @staticmethod
    async def _get_response_body(request: Request) -> Any:
        from json import JSONDecodeError
        try:
            return await request.json()
        except JSONDecodeError:
            return await request.body()

    async def dispatch(self, request: Request, call_next):
        request_body = await self._get_response_body(request)
        base_log_message = f'{request.method} {request.url} | body={request_body} | params={request.query_params} | path_params={request.path_params} | headers={request.headers}'
        try:
            response = await call_next(request)
            logger.debug(f'[OK] {base_log_message}')
        except Exception as exp:
            logger.debug(f'[ERROR] {base_log_message}. Error message: {exp}')
            raise exp

        return response

