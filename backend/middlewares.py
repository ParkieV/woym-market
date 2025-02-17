import logging
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from logs import backend_logger



class EndpointLoggingMiddleware(BaseHTTPMiddleware):
    # def __init__(self, backend, *args, **kwargs):
    #     super().__init__(backend, *args, **kwargs)

    @staticmethod
    async def _get_response_body(request: Request) -> Any:
        if 'multipart/form-data' in request.headers.get('content-type', ''):
            return None
        try:
            return await request.json()
        except Exception:
            return await request.body()

    async def dispatch(self, request: Request, call_next):
        request_body = await self._get_response_body(request)
        base_log_message = f'{request.method} {request.url} | body={request_body} | params={request.query_params} | path_params={request.path_params} | headers={dict(request.headers.items())}'
        try:
            response = await call_next(request)
            backend_logger.debug(f'[OK] {base_log_message}')
        except Exception as exp:
            backend_logger.debug(f'[ERROR] {base_log_message}. Error message: {exp}')
            raise exp

        return response

