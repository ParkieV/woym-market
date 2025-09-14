import time
from asyncio import iscoroutinefunction
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from logs import backend_logger

P = ParamSpec('P')
R = TypeVar('R')


def timer(func: Callable[P, R | Awaitable[R]]) -> Callable[P, R | Awaitable[R]]:
    """Декоратор для логгирования времени выполнения функции"""

    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            func_path = f'{func.__module__}.{func.__qualname__}'
            backend_logger.info('%s complete duration for %.6f seconds', func_path, duration)
            return result

    else:

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            backend_logger.info('%s complete duration for %.6f seconds', func.__name__, duration)
            return result

    return wrapper
