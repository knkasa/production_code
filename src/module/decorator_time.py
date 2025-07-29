import time
from functools import wraps
from loguru import logger

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} executed in {end-start:.1f} seconds")
        return result
    return wrapper