
import logging
import os
import json
from logging.handlers import TimedRotatingFileHandler
import sys

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        # Load config
        config_path = "/data/chats/p6wyr/workspace/config/config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            log_config = config.get("logging", {})
            log_level = log_config.get("level", "INFO")
            log_file = log_config.get("file_path", "/data/chats/p6wyr/workspace/logs/app.log")
            log_rotation = log_config.get("rotation", "1 day")
        else:
            log_level = "INFO"
            log_file = "/data/chats/p6wyr/workspace/logs/app.log"
            log_rotation = "1 day"
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("ebay_price_predictor")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="d",
            interval=1,
            backupCount=30
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
    
    def get_logger(self):
        return self.logger

# Example usage
# from utils.logger import Logger
# logger = Logger().get_logger()
# logger.info("This is an info message")
# logger.error("This is an error message")
