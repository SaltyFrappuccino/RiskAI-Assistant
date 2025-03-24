"""
Модуль содержит агента для проверки соответствия кода лучшим практикам.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.best_practices_agent
from models.agent_schemas import BestPracticesResult

# Настройка логирования
logger = logging.getLogger(__name__)


class BestPracticesAgent(CodeAnalysisAgent):
    """
    Агент для проверки соответствия кода лучшим практикам.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(
            gigachat_service=gigachat_service, 
            prompt=prompts.best_practices_agent.prompt,
            result_schema=BestPracticesResult
        ) 