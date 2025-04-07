"""
Модуль для конфигурации приложения.
Загружает переменные окружения из .env файла.
"""
import os
from dotenv import load_dotenv

load_dotenv()

AUTH_KEY = os.getenv("AUTH_KEY")
AUTH_URL = os.getenv("AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
GIGA_URL = os.getenv("GIGA_URL", "https://gigachat.devices.sberbank.ru/api/v1")
MODEL = os.getenv("MODEL", "GigaChat-2-Pro")

PORT = int(os.getenv("PORT", 8080))

DEFAULT_STORY = "Требуется реализовать функционал согласно требованиям."
DEFAULT_REQUIREMENTS = "Не предоставлены конкретные требования."
DEFAULT_CODE = "# Код не предоставлен"
DEFAULT_TEST_CASES = "# Тест-кейсы не предоставлены"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 