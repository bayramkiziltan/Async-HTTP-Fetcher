import time
import functools
import logging
import inspect

def timer(log_level=logging.INFO):
    def decorator(func):
        logger = logging.getLogger(func.__module__)
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start
                    logger.log(log_level, f"[async] {func.__name__} took {duration:.4f} s")
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start
                    logger.log(log_level, f"{func.__name__} took {duration:.4f} s")
            return sync_wrapper
    return decorator
