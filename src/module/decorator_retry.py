from functools import wraps
from loguru import logger
import time

def retry(max_try:int=3, delay:int=10, exceptions=(RuntimeError, TimeoutError)):
    def decorator_retry(func):
        @wraps(func)
        def wrapper_retry(*args, **kwargs):
            tries = 0
            while tries < max_try:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    tries += 1
                    if tries==max_try:
                        raise e
                    logger.error(f"Attempt {tries} failed. Retrying...")
                    time.sleep(delay)
        return wrapper_retry
    return decorator_retry