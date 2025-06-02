import logging
import time
from contextlib import contextmanager

@contextmanager
def log_time(label: str, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
    start = time.perf_counter()
    exc = None
    try:
        yield
    except Exception as e:
        exc = e
        raise
    finally:
        duration = time.perf_counter() - start
        logger.info(f"{label} finished in {duration:.4f}s" + (f" (exc: {exc})" if exc else ""))

class LogTime:
    def __init__(self, label: str, logger=None):
        self.label = label
        self.logger = logger or logging.getLogger(__name__)
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start
        msg = f"{self.label} finished in {duration:.4f}s"
        if exc_type is not None:
            msg += f" (exc: {exc_val})"
        self.logger.info(msg)
        return False
