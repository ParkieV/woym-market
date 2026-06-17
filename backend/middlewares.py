import logging
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from logs import backend_logger
from metrics import HTTP_ERRORS_TOTAL, HTTP_REQUEST_DURATION, HTTP_REQUESTS_TOTAL



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


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            HTTP_ERRORS_TOTAL.labels(
                path=self._route_path(request),
                error_type=type(exc).__name__,
            ).inc()
            raise
        finally:
            path = self._route_path(request)
            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()
            HTTP_REQUEST_DURATION.labels(method=method, path=path).observe(
                time.perf_counter() - start
            )

    @staticmethod
    def _route_path(request: Request) -> str:
        route = request.scope.get("route")
        return route.path if route else request.url.path
