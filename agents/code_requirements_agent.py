"""
Модуль содержит агента для проверки соответствия кода требованиям.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.code_requirements_agent

# Настройка логирования
logger = logging.getLogger(__name__)


class CodeRequirementsAgent(CodeAnalysisAgent):
    """
    Агент для проверки соответствия кода требованиям.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(gigachat_service, prompts.code_requirements_agent.prompt) 