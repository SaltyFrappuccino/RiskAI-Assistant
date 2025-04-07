"""
Модуль содержит базовый класс агента для анализа кода.
"""
import logging
from typing import Dict, Any, Type

from pydantic import BaseModel
from services.gigachat_service import GigaChatService

logger = logging.getLogger(__name__)


class CodeAnalysisAgent:
    """
    Базовый класс агента для анализа кода.
    """

    def __init__(self, gigachat_service: GigaChatService, prompt: str, result_schema: Type[BaseModel] = None):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
            prompt: Промпт для агента.
            result_schema: Схема для результата анализа (Pydantic модель).
        """
        self.gigachat_service = gigachat_service
        self.prompt = prompt
        self.result_schema = result_schema
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение анализа данных.
        
        Args:
            data: Данные для анализа.
            
        Returns:
            Dict[str, Any]: Результат анализа.
        """
        logger.info(f"Запуск агента {self.__class__.__name__}")
        
        if self.result_schema:
            result = self.gigachat_service.call_agent_with_function(self.prompt, data, self.result_schema)
        else:
            result = self.gigachat_service.call_agent_with_prompt(self.prompt, data)
            
        logger.info(f"Агент {self.__class__.__name__} завершил работу")
        return result 