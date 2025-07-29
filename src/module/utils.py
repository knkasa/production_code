import os
import pdb
import time
from loguru import logger
from .monitoring import SystemMonitor
from .model1 import model1
from .model2 import model2
from src.module.decorator_time import measure_time

class utility:
    def __init__(self, config:dict) -> None:
        logger.info('Initializing modules...')
        self.system_monitor = SystemMonitor(log_interval=int(os.getenv('LOG_INTERVAL')))
        self.model1 = model1()
        self.model2 = model2()
        self.config = config

    def __str__(self): 
        return f"Attribute vars:{self.monitor}, {self.model1}"
    
    def _model1(self):
        self.model1.run(self.config)

    def _model2(self):
        self.model2.run(self.config)

    def invalid_request(self):
        logger.exception("Model name invalid.")

    def model_dict(self, request_type):
        request_handlers = {
            "model1": self._model1,
            "model2": self._model2,
            }
        handler = request_handlers.get(request_type, self.invalid_request)
        handler()

    @staticmethod
    @measure_time
    def decorator_test():
        logger.debug("Testing decorator...")
        time.sleep(1)