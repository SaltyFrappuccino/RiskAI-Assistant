"""
Модуль для взаимодействия с GigaChat API.
"""
import json
import logging
import re
from typing import Dict, Any, List, Type

from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_gigachat.tools.giga_tool import giga_tool as GigaChatTool
from pydantic import BaseModel, Field

import config

# Настройка логирования
logger = logging.getLogger(__name__)


class GigaChatService:
    """
    Сервис для взаимодействия с GigaChat API.
    """

    def __init__(self):
        """
        Инициализация сервиса GigaChat.
        """
        self.giga = None
        self.init_giga()

    def init_giga(self):
        """
        Инициализация клиента GigaChat.
        """
        try:
            logger.info("Инициализация GigaChat клиента")
            self.giga = GigaChat(
                credentials=config.AUTH_KEY,
                base_url=config.GIGA_URL if config.GIGA_URL else None,
                auth_url=config.AUTH_URL if config.AUTH_URL else None,
                model=config.MODEL,
                verify_ssl_certs=False,
            )
            logger.info("GigaChat клиент успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации GigaChat клиента: {e}")
            raise

    def extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Извлечение JSON из текстового ответа.
        
        Args:
            text: Текстовый ответ, содержащий JSON.
            
        Returns:
            Dict[str, Any]: Извлеченный JSON или словарь с ошибкой.
        """
        try:
            # Удаляем все, что находится до начала JSON-объекта
            json_match = re.search(r'({[\s\S]*})', text)
            
            if json_match:
                json_text = json_match.group(1)
                # Проверяем, является ли текст валидным JSON
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    # Если этот текст не валидный JSON, ищем JSON внутри маркеров ```json
                    code_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
                    if code_blocks:
                        for block in code_blocks:
                            try:
                                return json.loads(block.strip())
                            except json.JSONDecodeError:
                                continue
            
            # Если JSON не найден, возвращаем значения по умолчанию для метрик
            logger.warning("Не удалось извлечь JSON из ответа GigaChat. Возвращаем значения по умолчанию.")
            return {
                "metrics": {
                    "code_requirements_match": 0.0,
                    "test_requirements_match": 0.0,
                    "test_code_match": 0.0
                },
                "bugs": [],
                "vulnerabilities": [],
                "recommendations": [],
                "summary": "Не удалось извлечь результаты анализа. Пожалуйста, попробуйте еще раз."
            }
        except Exception as e:
            logger.error(f"Ошибка при извлечении JSON: {e}")
            return {
                "metrics": {
                    "code_requirements_match": 0.0,
                    "test_requirements_match": 0.0,
                    "test_code_match": 0.0
                },
                "error": str(e)
            }

    def call_agent_with_prompt(self, prompt: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вызов агента с заданным промптом и данными.
        
        Args:
            prompt: Промпт для агента.
            data: Данные для заполнения промпта.
            
        Returns:
            Dict[str, Any]: Результат работы агента в формате JSON.
        """
        try:
            # Заполнение промпта данными
            filled_prompt = prompt.format(**data)
            
            # Создание сообщения системы
            system_message = SystemMessage(content=filled_prompt)
            
            # Создание сообщения пользователя
            human_message = HumanMessage(content="Выполни анализ предоставленных данных и верни результат в формате JSON.")
            
            # Вызов модели
            logger.info("Вызов GigaChat для анализа")
            response = self.giga.invoke([system_message, human_message])
            
            # Извлечение JSON из ответа
            response_text = response.content
            
            # Используем улучшенный метод извлечения JSON
            result = self.extract_json_from_text(response_text)
            
            if "error" not in result:
                logger.info("Успешно получен результат анализа в формате JSON")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при вызове агента: {e}")
            return {
                "metrics": {
                    "code_requirements_match": 0.0,
                    "test_requirements_match": 0.0,
                    "test_code_match": 0.0
                },
                "error": str(e)
            }

    def call_agent_with_function(self, prompt: str, data: Dict[str, Any], result_schema: Type[BaseModel]) -> Dict[str, Any]:
        """
        Вызов агента с заданным промптом, данными и схемой ожидаемого результата.
        
        Args:
            prompt: Промпт для агента.
            data: Данные для заполнения промпта.
            result_schema: Схема ожидаемого результата.
            
        Returns:
            Dict[str, Any]: Результат работы агента в формате JSON.
        """
        try:
            # Используем простой текстовый запрос вместо функций, так как функции могут привести к ошибке
            # 'properties.kwargs.properties' is missing
            
            # Добавим в промпт информацию о требуемой структуре ответа
            schema_json = json.dumps(result_schema.model_json_schema(), ensure_ascii=False, indent=2)
            schema_info = f"\n\nОтвет должен соответствовать следующей JSON-схеме:\n```json\n{schema_json}\n```\n"
            
            # Заполнение промпта данными
            filled_prompt = prompt.format(**data) + schema_info
            
            # Создание системного сообщения
            system_message = SystemMessage(content=filled_prompt)
            human_message = HumanMessage(content="Выполни анализ предоставленных данных и верни результат в формате JSON в соответствии с указанной схемой.")
            
            # Текстовый запрос без функций
            logger.info(f"Вызов GigaChat в текстовом режиме, ожидаемая схема: {result_schema.__name__}")
            response = self.giga.invoke([system_message, human_message])
            
            # Извлечение JSON из ответа
            response_text = response.content
            result = self.extract_json_from_text(response_text)
            
            if "error" not in result:
                logger.info("Успешно получен результат анализа в формате JSON")
            else:
                logger.warning(f"Ошибка при извлечении результата: {result.get('error')}")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при вызове агента с функцией: {e}")
            return {
                "metrics": {
                    "code_requirements_match": 0.0,
                    "test_requirements_match": 0.0,
                    "test_code_match": 0.0
                },
                "error": str(e)
            } 