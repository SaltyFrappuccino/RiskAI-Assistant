"""
Модуль содержит агента для обнаружения багов в коде.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.bug_detector_agent
from models.agent_schemas import BugDetectorResult

# Настройка логирования
logger = logging.getLogger(__name__)


class BugDetectorAgent(CodeAnalysisAgent):
    """
    Агент для обнаружения багов в коде.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(
            gigachat_service=gigachat_service, 
            prompt=prompts.bug_detector_agent.prompt, 
            result_schema=BugDetectorResult
        ) 