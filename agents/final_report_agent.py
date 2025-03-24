"""
Модуль содержит агента для формирования итогового отчета.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.final_report_agent

# Настройка логирования
logger = logging.getLogger(__name__)


class FinalReportAgent(CodeAnalysisAgent):
    """
    Агент для формирования итогового отчета.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(gigachat_service, prompts.final_report_agent.prompt) 