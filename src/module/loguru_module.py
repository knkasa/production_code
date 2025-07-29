import os
from datetime import datetime
from loguru import logger

class loguru_class:
    def __init__(self):
        if not os.path.exists('log'):
            os.makedirs('log')
        logger.add(
            f"./log/monitoring_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log", 
            rotation="100MB",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}"
            )
        
        logger.info('logger initialized.')