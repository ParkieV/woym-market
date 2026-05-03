import asyncio
from collections.abc import Callable, Awaitable, AsyncIterator
from functools import wraps
from typing import ParamSpec, TypeVar

from aiolimiter import AsyncLimiter

P = ParamSpec('P')
R = TypeVar('R')


def rate_limiter(
        max_rate: int = 1, period: int = 1, interval: float | None = None
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    limiter = AsyncLimiter(max_rate, secs)

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> R:
            async with limiter:
                result = await func(*args, **kwargs)
                if interval is not None:
                    await asyncio.sleep(interval)
                return result

        return wrapper

    return decorator


def rate_limiter_gen(max_rate: int = 1, secs: int = 1):
    limiter = AsyncLimiter(max_rate, secs)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            agen = func(*args, **kwargs)
            try:
                while True:
                    async with limiter:
                        item = await agen.__anext__()   # лимитируем каждый шаг
                    yield item
            except StopAsyncIteration:
                return
        return wrapper

    return decorator