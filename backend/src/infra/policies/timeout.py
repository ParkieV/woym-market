import asyncio
import functools
import inspect
import signal

class DeadlineExceededError(TimeoutError):
    pass

def timeout(seconds: float):
    def decorator(fn):
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*a, **kw):
                try:
                    return await asyncio.wait_for(fn(*a, **kw), timeout=seconds)
                except asyncio.TimeoutError as e:
                    raise DeadlineExceededError(f"{fn.__name__} превысила {seconds} сек") from e
            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(*a, **kw):
                def handler(signum, frame):
                    raise DeadlineExceededError(f"{fn.__name__} превысила {seconds} сек")
                old = signal.signal(signal.SIGALRM, handler)
                signal.alarm(int(seconds))
                try:
                    return fn(*a, **kw)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old)
            return sync_wrapper
    return decorator