import pdb
import os
from typing import Tuple
from loguru import logger
import pandas as pd
from ..enum_list import SYSTEMS

class data_loader:
    def __init__(self):
        pass
    @classmethod
    def load_data(cls, config:dict) -> Tuple[pd.DataFrame, pd.Series]:
        """
            Load dataset.

            Args:
                config: コンフィグファイル
            Return:
                Input data, Target data 
        """
        try:
            logger.info("Loading dataset.")
            if SYSTEMS.mode==SYSTEMS('local'):
                df = pd.read_parquet(os.path.join('data', config['data']['file']))
                return df.iloc[:, :-1], df.iloc[:, -1]
        except Exception as e:
            logger.exception("Error at data_loader.load_data:")