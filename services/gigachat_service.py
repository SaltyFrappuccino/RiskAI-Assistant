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
                verify_ssl_certs=False            
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
            json_match = re.search(r'({[\s\S]*})', text)
            
            if json_match:
                json_text = json_match.group(1)
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    code_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
                    if code_blocks:
                        for block in code_blocks:
                            try:
                                return json.loads(block.strip())
                            except json.JSONDecodeError:
                                continue
            
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

    def call_agent_with_prompt(self, prompt: str, data: Dict[str, Any]) -> Any:
        """
        Вызов агента с заданным промптом и данными.
        
        Args:
            prompt: Промпт для агента.
            data: Данные для заполнения промпта.
            
        Returns:
            Any: Результат работы агента (текст или словарь с JSON).
        """
        try:
            filled_prompt = prompt.format(**data)
            system_message = SystemMessage(content=filled_prompt)
            is_preprocessor = 'field_type' in data and 'text' in data
            
            if is_preprocessor:
                human_message = HumanMessage(content="Обработай предоставленный текст и верни обработанный результат.")
            else:
                human_message = HumanMessage(content="Выполни анализ предоставленных данных и верни результат в формате JSON.")
            
            logger.info("Вызов GigaChat для анализа")
            response = self.giga.invoke([system_message, human_message])
            
            response_text = response.content
            
            if is_preprocessor:
                return response_text
            
            result = self.extract_json_from_text(response_text)
            
            if "error" not in result:
                logger.info("Успешно получен результат анализа в формате JSON")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при вызове агента: {e}")
            
            if 'field_type' in data and 'text' in data:
                return data.get('text', '')
                
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
        max_attempts = 3
        base_delay = 2
        
        for attempt in range(max_attempts):
            try:
                schema_json = json.dumps(result_schema.model_json_schema(), ensure_ascii=False, indent=2)
                schema_info = f"\n\nОтвет должен соответствовать следующей JSON-схеме:\n```json\n{schema_json}\n```\n"
                
                filled_prompt = prompt.format(**data) + schema_info
                
                system_message = SystemMessage(content=filled_prompt)
                human_message = HumanMessage(content="Выполни анализ предоставленных данных и верни результат в формате JSON в соответствии с указанной схемой.")
                
                logger.info(f"Вызов GigaChat в текстовом режиме (попытка {attempt+1}/{max_attempts}), ожидаемая схема: {result_schema.__name__}")
                response = self.giga.invoke([system_message, human_message])
                
                response_text = response.content
                result = self.extract_json_from_text(response_text)
                
                if "error" not in result:
                    logger.info("Успешно получен результат анализа в формате JSON")
                    return result
                else:
                    logger.warning(f"Ошибка при извлечении результата: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Ошибка при вызове агента (попытка {attempt+1}/{max_attempts}): {e}")
                
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                logger.info(f"Повторная попытка через {delay} секунд...")
                import time
                time.sleep(delay)
        
        logger.error(f"Все {max_attempts} попытки вызова агента завершились неудачно")
        return {
            "metrics": {
                "code_requirements_match": 0.0,
                "test_requirements_match": 0.0,
                "test_code_match": 0.0
            },
            "error": f"Не удалось получить ответ от GigaChat после {max_attempts} попыток"
        } 