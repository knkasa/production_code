# -*- coding: utf-8 -*-
import os
import pdb
from typing import List
from dotenv import load_dotenv
import yaml
from loguru import logger

class file_loader:
    def __init__(self):
        logger.info("Initializing file_loader.")

    def load_config(self, options:List[str]) -> dict:
        """Get yaml file."""
        config_file = 'config.yaml'
        for n, opt in enumerate(options):
            if opt[0]=='--config_file' or opt[0]=='-c':
                config_file = opt[1]
            elif opt[0]=='--text_file' or opt[0]=='-t':
                text_file = opt[1]
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"YAML file not found: {config_file}")
        
        config = self.load_config_with_encoding(config_file)
        return config

    def load_config_with_encoding(self, config_file:dict) -> None:
        """Load yaml file."""
        for encoding in self._encoding_optons():
            try:
                with open(config_file, 'r', encoding=encoding) as yml:
                    return yaml.safe_load(yml)
                logger.debug(f"The following encoding worked. {encoding}")
                break
            except UnicodeDecodeError:
                continue
        raise Exception("Loading yaml failed. Try different encoding.")
            
    def load_env(self) -> None:
        """Load env file."""
        for encoding in self._encoding_optons():
            try:
                load_dotenv(encoding=encoding, verbose=True)
                logger.debug(f"The following encoding worked. {encoding}")
                return None
            except UnicodeDecodeError:
                continue
        raise Exception("Loading .env failed. Try different encoding.")
    
    def _encoding_optons(self) -> List[str]:
        return ['Shift-JIS','UTF-8', 'CP932']
