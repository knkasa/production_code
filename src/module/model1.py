import pdb
import os
from loguru import logger
import numpy as np
import pandas as pd
from .data_load import data_loader
from .lightgbm_engine import LightGBMRegressorTuner

class model1:
    def __init__(self):
        logger.info('model1 loaded.')
        self.tuner = LightGBMRegressorTuner()

    def run(self, config:dict) -> None:
        """ Model1の構築 """
        try:
            df_input, target_data = data_loader.load_data(config)
            self.tuner.preprocessing(df_input, target_data, config)
            self.tuner.tune()
            logger.info(f"Best Params: {self.tuner.best_params}")
            self.tuner.train_final_model()
            self.tuner.evaluate(config)

        except Exception as e:
            logger.exception(f"Error at model1.run:")
        