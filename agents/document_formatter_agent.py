"""
Агент для форматирования документов по шаблону с возможностью диалога.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from models.data_models import DocumentFormatterResult, FormatterMessage, CacheStatistics
from services.gigachat_service import GigaChatService
from services.cache_service import CacheService
from agents.base_agent import CodeAnalysisAgent

logger = logging.getLogger(__name__)

class DocumentFormatterAgent:
    """
    Агент для форматирования документов по шаблону/правилам с возможностью
    интерактивного диалога для уточнения недостающей информации.
    """
    
    def __init__(self, 
                 gigachat_service: GigaChatService,
                 cache_service: Optional[CacheService] = None):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для работы с GigaChat
            cache_service: Сервис для работы с кэшем
        """
        self.gigachat_service = gigachat_service
        self.cache_service = cache_service
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """
        Создает системный промпт для агента.
        
        Returns:
            str: Системный промпт
        """
        return """
        Ты - профессиональный ассистент по форматированию документов согласно заданным шаблонам и правилам.
        
        Твоя задача - форматировать предоставленный документ в соответствии с заданным шаблоном/правилами.
        
        ВАЖНО: Если тебе не хватает какой-либо информации для форматирования документа, ты должен задать
        уточняющие вопросы пользователю. Не придумывай информацию самостоятельно!
        
        Процесс работы:
        1. Проанализируй шаблон/правила и определи, какая информация нужна для форматирования.
        2. Проанализируй предоставленный документ и выдели из него всю доступную информацию.
        3. Если тебе не хватает информации, задай конкретные вопросы пользователю.
        4. На основе полученных ответов и исходного документа создай отформатированную версию.
        5. Если информации все еще не хватает, четко укажи это в результате.
        
        Формат ответа:
        - В начале предоставь текущую версию отформатированного документа (на основе имеющейся информации).
        - Если нужна дополнительная информация, задай конкретные вопросы.
        """
    
    async def format_document(self, 
                              template_rules: str, 
                              document_content: str, 
                              use_cache: bool = True,
                              conversation_history: Optional[List[FormatterMessage]] = None) -> DocumentFormatterResult:
        """
        Форматирует документ в соответствии с шаблоном/правилами.
        
        Args:
            template_rules: Шаблон или набор правил для форматирования
            document_content: Содержимое документа, которое нужно отформатировать
            use_cache: Использовать ли кэш
            conversation_history: История диалога с пользователем
            
        Returns:
            DocumentFormatterResult: Результат форматирования
        """
        if conversation_history is None:
            conversation_history = []
            # Начальное сообщение от пользователя
            conversation_history.append(FormatterMessage(
                role="user",
                content=f"Шаблон/правила: {template_rules}\n\nДокумент для форматирования: {document_content}",
                timestamp=datetime.now()
            ))
        
        cache_stats = CacheStatistics()
        
        # Подготовка сообщений для запроса к модели
        messages = [{"role": "system", "content": self.system_prompt}]
        
        for msg in conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Запрос к модели
        response = await self.gigachat_service.chat_completion(messages)
        
        # Получаем содержимое сообщения из ответа в формате словаря
        assistant_message = response["choices"][0]["message"]["content"]
        
        # Добавление ответа ассистента в историю диалога
        conversation_history.append(FormatterMessage(
            role="assistant",
            content=assistant_message,
            timestamp=datetime.now()
        ))
        
        # Определение, требуются ли еще уточнения
        is_completed, missing_info, formatted_content, comments = self._process_assistant_response(assistant_message)
        
        return DocumentFormatterResult(
            formatted_content=formatted_content,
            is_completed=is_completed,
            missing_information=missing_info,
            conversation_history=conversation_history,
            comments=comments,
            cache_stats=cache_stats
        )
    
    def _process_assistant_response(self, assistant_message: str) -> Tuple[bool, List[str], str, Optional[str]]:
        """
        Обрабатывает ответ от модели и извлекает из него информацию.
        
        Args:
            assistant_message: Ответ от модели
            
        Returns:
            tuple: (is_completed, missing_info, formatted_content, comments)
        """
        missing_info = []
        comments = None
        is_completed = True
        
        # Извлекаем форматированный контент из ответа модели
        formatted_content = assistant_message
        
        # Проверяем, есть ли уточняющие вопросы
        if "?" in assistant_message:
            # Если в ответе есть вопросы, считаем, что форматирование не завершено
            is_completed = False
            
            # Пытаемся выделить вопросы как missing_info
            lines = assistant_message.split("\n")
            for line in lines:
                if "?" in line and len(line.strip()) > 10:
                    missing_info.append(line.strip())
        
        # Если в ответе есть явное указание на окончательный результат, считаем его завершенным
        if "окончательн" in assistant_message.lower() or "финальн" in assistant_message.lower():
            is_completed = True
            # Пытаемся выделить комментарии
            if "Комментари" in assistant_message:
                comment_parts = assistant_message.split("Комментари")
                if len(comment_parts) > 1:
                    comments = "Комментари" + comment_parts[1]
        
        return is_completed, missing_info, formatted_content, comments
    
    async def add_user_message(self, 
                              user_message: str, 
                              conversation_history: List[FormatterMessage],
                              template_rules: str, 
                              document_content: str, 
                              use_cache: bool = True) -> DocumentFormatterResult:
        """
        Добавляет сообщение пользователя в диалог и получает новый ответ.
        
        Args:
            user_message: Сообщение пользователя
            conversation_history: История диалога
            template_rules: Шаблон или правила форматирования
            document_content: Содержимое документа
            use_cache: Использовать ли кэш
            
        Returns:
            DocumentFormatterResult: Обновленный результат форматирования
        """
        # Добавляем сообщение пользователя в историю
        conversation_history.append(FormatterMessage(
            role="user",
            content=user_message,
            timestamp=datetime.now()
        ))
        
        # Получаем обновленный результат
        return await self.format_document(
            template_rules=template_rules,
            document_content=document_content,
            use_cache=use_cache,
            conversation_history=conversation_history
        )