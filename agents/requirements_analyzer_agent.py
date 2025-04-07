"""
Модуль содержит агента для анализа требований на их состоятельность и компетентность.
"""
import logging
from typing import Dict, Any, List, Optional

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
from agents.rag_processor import RAGProcessor
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
        self.rag_processor = RAGProcessor(gigachat_service)
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ требований на их состоятельность и компетентность.
        
        Args:
            data: Данные для анализа, содержащие требования.
                
        Returns:
            Dict[str, Any]: Результат анализа требований.
        """
        logger.info("Запуск анализа требований")
        
        requirements = data.get("requirements", "")
        guidelines = data.get("guidelines", "")
        
        # Проверка размера текста требований
        # Примерно 5000 символов - это размер, который может вызвать проблемы
        large_text_threshold = 5000
        
        if len(requirements) > large_text_threshold:
            logger.info(f"Обнаружен большой текст требований ({len(requirements)} символов), применяем RAG")
            
            # Подготовка дополнительных данных для промпта
            additional_data = {
                "guidelines": guidelines,
                # По умолчанию chunk_info пустая строка
                "chunk_info": ""
            }
            
            # Анализ с использованием RAG
            result = self.rag_processor.analyze_with_rag(
                prompt_template=self.prompt,
                text=requirements,
                result_schema=self.result_schema,
                additional_data=additional_data,
                chunk_size=4000  # Примерно 4000 символов на чанк
            )
            
            logger.info("Анализ требований с использованием RAG успешно завершен")
            return result
        else:
            # Для небольших текстов используем обычный анализ
            logger.info(f"Размер текста требований ({len(requirements)} символов) позволяет анализировать его целиком")
            
            # Подготовка данных для промпта
            prompt_data = {
                "requirements": requirements,
                "guidelines": guidelines,
                "chunk_info": ""  # Пустая строка для полного текста
            }
            
            # Вызов LLM через сервис с использованием структурированного вывода
            try:
                # Используем метод с Pydantic-моделью для структурированного вывода
                result = self.gigachat_service.call_with_structured_output(
                    prompt=self.prompt,
                    data=prompt_data,
                    result_schema=self.result_schema
                )
                
                logger.info("Анализ требований успешно завершен")
                return result
            except Exception as e:
                logger.error(f"Ошибка при анализе требований: {str(e)}")
                raise 