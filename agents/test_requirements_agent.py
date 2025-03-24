"""
Модуль содержит агента для проверки соответствия тест-кейсов требованиям.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.test_requirements_agent
from models.agent_schemas import TestRequirementsResult

# Настройка логирования
logger = logging.getLogger(__name__)


class TestRequirementsAgent(CodeAnalysisAgent):
    """
    Агент для проверки соответствия тест-кейсов требованиям.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(
            gigachat_service=gigachat_service, 
            prompt=prompts.test_requirements_agent.prompt,
            result_schema=TestRequirementsResult
        ) 