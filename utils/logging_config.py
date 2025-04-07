"""
Модуль для настройки логирования.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler

import config


def setup_logging():
    """
    Настройка логирования для приложения.
    """
    log_level_name = config.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    root_logger.handlers = []
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        "app.log", maxBytes=10485760, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    logging.info("Логирование настроено с уровнем %s", log_level_name) 