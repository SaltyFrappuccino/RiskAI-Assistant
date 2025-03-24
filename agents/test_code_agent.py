"""
Модуль содержит агента для проверки соответствия тест-кейсов коду.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.test_code_agent

# Настройка логирования
logger = logging.getLogger(__name__)


class TestCodeAgent(CodeAnalysisAgent):
    """
    Агент для проверки соответствия тест-кейсов коду.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(gigachat_service, prompts.test_code_agent.prompt) 