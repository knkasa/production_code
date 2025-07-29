from loguru import logger
from sklearn.linear_model import LinearRegression

class model2:
    def __init__(self):
        logger.info('model2 loaded.')

    def __str__(self): 
        return f"Attribute vars: "

    def run(self):
        try:
            pass
        except Exception as e:
            logger.exception(f"Error at model2.run:")
