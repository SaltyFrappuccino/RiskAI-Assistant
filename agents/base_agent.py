"""
Модуль содержит базовый класс агента для анализа кода.
"""
import logging
from typing import Dict, Any

from services.gigachat_service import GigaChatService

# Настройка логирования
logger = logging.getLogger(__name__)


class CodeAnalysisAgent:
    """
    Базовый класс агента для анализа кода.
    """

    def __init__(self, gigachat_service: GigaChatService, prompt: str):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
            prompt: Промпт для агента.
        """
        self.gigachat_service = gigachat_service
        self.prompt = prompt
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение анализа данных.
        
        Args:
            data: Данные для анализа.
            
        Returns:
            Dict[str, Any]: Результат анализа.
        """
        logger.info(f"Запуск агента {self.__class__.__name__}")
        result = self.gigachat_service.call_agent_with_prompt(self.prompt, data)
        logger.info(f"Агент {self.__class__.__name__} завершил работу")
        return result 