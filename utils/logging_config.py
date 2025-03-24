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
    # Получение уровня логирования из конфигурации
    log_level_name = config.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Создание форматтера для логов
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Очистка существующих обработчиков
    root_logger.handlers = []
    
    # Добавление обработчика для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Добавление обработчика для записи в файл
    file_handler = RotatingFileHandler(
        "app.log", maxBytes=10485760, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Настройка логирования для внешних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Вывод информации о настройке логирования
    logging.info("Логирование настроено с уровнем %s", log_level_name) 