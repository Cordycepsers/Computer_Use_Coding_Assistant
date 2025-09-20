import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "/home/computeruse/logs/app.log",
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """Set up comprehensive logging configuration"""
    
    # Create logger
    logger = logging.getLogger('coding_assistant')
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers = []
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger
