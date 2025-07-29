# -*- coding: utf-8 -*-
import os
import pdb
import time
import sys
from pathlib import Path
import getopt
from loguru import logger
from .enum_list import SYSTEMS
from .module.loguru_module import loguru_class
from .module.file_loader import file_loader
from .module.utils import utility

def main() -> None:
    try:
        time1 = time.perf_counter()
        loguru_class()
        
        logger.info('Program starting...')
        system_path = Path('__file__').resolve().parent
        logger.info(f'system path:{system_path}')
        
        #if is_system_path:=Path('src').is_dir():
        #    logger.info(f'Current working directory:{system_path}')
        #else:
        #    logger.error(f'Correct system path:{is_system_path}.  Exiting...')
        #    exit()

        options, _ = getopt.getopt(sys.argv[1:], 'c:t:', ['config_file=', 'text_file='])

        loader_class = file_loader()
        config = loader_class.load_config(options)
        loader_class.load_env()

        util_engine = utility(config)
        util_engine.decorator_test()

        if SYSTEMS.mode==SYSTEMS('local'):
            logger.info("Running in local.")
            loader_class.load_env()
        
        logger.info(f"model:{config['model']}")
        
        if config['monitoring']: 
            logger.info(f"Log interval:{os.getenv('LOG_INTERVAL')}")
            util_engine.system_monitor.start_monitoring()
        else:
            logger.info(f"Monitering off")
        
        util_engine.model_dict(config['model'])

        logger.info(f"Job finished. Elaplsed time:{(time.perf_counter()-time1):.2f}")
                    
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt.  Program stopping.")
    except Exception as e:
        logger.exception(f"Exceiption.")
    finally:
        logger.info("Log closing.")
        util_engine.system_monitor.stop_monitoring()

if __name__=='__main__':
    main()