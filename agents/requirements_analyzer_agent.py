"""
Модуль содержит агента для анализа требований на их состоятельность и компетентность.
"""
import logging
from typing import Dict, Any, List, Optional

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.requirements_analyzer_agent
from models.agent_schemas import RequirementsAnalyzerResult

logger = logging.getLogger(__name__)


class RequirementsAnalyzerAgent(CodeAnalysisAgent):
    """
    Агент для анализа требований на их состоятельность и компетентность.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(
            gigachat_service=gigachat_service, 
            prompt=prompts.requirements_analyzer_agent.prompt,
            result_schema=RequirementsAnalyzerResult
        )
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ требований на их состоятельность и компетентность.
        
        Args:
            data: Данные для анализа, содержащие требования.
                
        Returns:
            Dict[str, Any]: Результат анализа требований.
        """
        logger.info("Запуск анализа требований")
        
        # Подготовка данных для промпта
        prompt_data = {
            "requirements": data.get("requirements", ""),
            "guidelines": data.get("guidelines", ""),
        }
        
        # Вызов LLM через сервис
        try:
            result = self.gigachat_service.call_agent_with_function(
                prompt=self.prompt,
                data=prompt_data,
                result_schema=self.result_schema
            )
            logger.info("Анализ требований успешно завершен")
            return result
        except Exception as e:
            logger.error(f"Ошибка при анализе требований: {str(e)}")
            raise 