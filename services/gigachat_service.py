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
                # Получаем JSON-схему из модели Pydantic
                schema_json = json.dumps(result_schema.model_json_schema(), ensure_ascii=False, indent=2)
                
                # Создаем более подробные инструкции для модели
                schema_info = f"\n\nОтвет должен строго соответствовать следующей JSON-схеме:\n```json\n{schema_json}\n```\n"
                schema_info += f"\nВажно! Ответ должен быть в формате JSON с правильными типами данных. Если в схеме указано, что поле должно быть object или array, не возвращай строки."
                
                # Проверка, содержит ли промпт пример структуры данных
                has_example = "```json" in prompt
                if not has_example:
                    schema_info += f"\n\nПример правильного формата ответа:\n```json\n{json.dumps(self._create_example_from_schema(result_schema), ensure_ascii=False, indent=2)}\n```"
                
                filled_prompt = prompt.format(**data) + schema_info
                
                system_message = SystemMessage(content=filled_prompt)
                human_message = HumanMessage(content="Выполни анализ предоставленных данных и верни результат в формате JSON в соответствии с указанной схемой. Убедись, что все поля имеют правильный формат и типы данных.")
                
                logger.info(f"Вызов GigaChat в текстовом режиме (попытка {attempt+1}/{max_attempts}), ожидаемая схема: {result_schema.__name__}")
                response = self.giga.invoke([system_message, human_message])
                
                response_text = response.content
                result = self.extract_json_from_text(response_text)
                
                if "error" not in result:
                    logger.info("Успешно получен результат анализа в формате JSON")
                    
                    # Проверяем наличие всех обязательных полей
                    model_fields = result_schema.model_fields
                    missing_fields = []
                    
                    for field_name, field in model_fields.items():
                        if field.is_required() and field_name not in result:
                            missing_fields.append(field_name)
                            # Добавляем значение по умолчанию
                            if field.annotation == float:
                                result[field_name] = 0.0
                            elif field.annotation == int:
                                result[field_name] = 0
                            elif field.annotation == str:
                                result[field_name] = ""
                            elif field.annotation == list or "List" in str(field.annotation):
                                result[field_name] = []
                            elif field.annotation == dict or "Dict" in str(field.annotation):
                                result[field_name] = {}
                    
                    if missing_fields:
                        logger.warning(f"В ответе модели отсутствуют обязательные поля: {missing_fields}")
                    
                    # Проверяем типы данных полей
                    for field_name, value in result.items():
                        if field_name in model_fields:
                            field = model_fields[field_name]
                            expected_type = field.annotation
                            
                            # Преобразование типов при необходимости
                            if "List" in str(expected_type) and isinstance(value, str):
                                logger.warning(f"Поле {field_name} ожидается списком, но получена строка. Попытка преобразования.")
                                try:
                                    result[field_name] = [value]
                                except Exception as e:
                                    logger.error(f"Ошибка при преобразовании поля {field_name}: {e}")
                            
                            if "Dict" in str(expected_type) and isinstance(value, str):
                                logger.warning(f"Поле {field_name} ожидается словарем, но получена строка. Попытка преобразования.")
                                try:
                                    result[field_name] = {"value": value}
                                except Exception as e:
                                    logger.error(f"Ошибка при преобразовании поля {field_name}: {e}")
                    
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
        
    def _create_example_from_schema(self, schema_class: Type[BaseModel]) -> Dict[str, Any]:
        """
        Создает пример данных на основе схемы Pydantic.
        
        Args:
            schema_class: Класс схемы Pydantic.
            
        Returns:
            Dict[str, Any]: Пример данных.
        """
        example = {}
        
        for field_name, field in schema_class.model_fields.items():
            if "float" in str(field.annotation).lower():
                example[field_name] = 75.5
            elif "int" in str(field.annotation).lower():
                example[field_name] = 42
            elif "str" in str(field.annotation).lower():
                example[field_name] = f"Пример текста для поля {field_name}"
            elif "List" in str(field.annotation):
                if "Dict" in str(field.annotation) or "dict" in str(field.annotation):
                    example[field_name] = [{"key": "value", "example": "value"}]
                elif "str" in str(field.annotation).lower():
                    example[field_name] = ["Пример элемента списка 1", "Пример элемента списка 2"]
                else:
                    example[field_name] = ["Пример элемента списка"]
            elif "Dict" in str(field.annotation) or "dict" in str(field.annotation):
                example[field_name] = {"key": "value", "example": "value"}
            else:
                example[field_name] = "Пример данных"
                
        return example

    async def chat_completion(self, messages: List[Dict[str, str]]) -> Any:
        """
        Асинхронный метод для работы с диалоговым интерфейсом.
        
        Args:
            messages: Список сообщений диалога в формате [{"role": "system", "content": "..."}, ...]
            
        Returns:
            Any: Результат диалога с моделью
        """
        try:
            logger.info("Отправка запроса на диалоговый чат-компплишн")
            
            # Отсортируем сообщения, чтобы system всегда был первым
            system_messages = [msg for msg in messages if msg["role"] == "system"]
            non_system_messages = [msg for msg in messages if msg["role"] != "system"]
            
            # Если нет системного сообщения, добавим дефолтное
            if not system_messages:
                system_messages = [{"role": "system", "content": "Ты - профессиональный ассистент по форматированию документов."}]
                
            # Объединяем сообщения, сначала system, затем остальные
            sorted_messages = system_messages + non_system_messages
            
            # Преобразуем в формат LangChain
            langchain_messages = []
            
            # Добавляем системное сообщение (всегда первое)
            langchain_messages.append(SystemMessage(content=sorted_messages[0]["content"]))
            
            # Добавляем остальные сообщения, чередуя user и assistant
            user_turn = True
            for msg in sorted_messages[1:]:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                    user_turn = False
                elif msg["role"] == "assistant":
                    # Так как в GigaChat API нет прямого способа добавить сообщение ассистента,
                    # мы эмулируем диалог парами сообщений
                    langchain_messages.append(HumanMessage(content=f"Пользователь получил от тебя ответ: \"{msg['content']}\". Теперь отвечай на следующий запрос пользователя."))
                    user_turn = True
            
            # Если последнее сообщение не от пользователя, добавляем запрос на продолжение
            if not user_turn:
                langchain_messages.append(HumanMessage(content="Продолжи диалог на основе предыдущих сообщений."))
            
            logger.info(f"Отправка {len(langchain_messages)} сообщений в GigaChat")
            response = self.giga.invoke(langchain_messages)
            
            # Формируем ответ в формате, совместимом с OpenAI API
            result = {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.content
                        },
                        "finish_reason": "stop",
                        "index": 0
                    }
                ]
            }
            
            logger.info("Успешно получен ответ от модели")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении chat completion: {e}")
            # Возвращаем минимальный формат ответа с сообщением об ошибке
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"Произошла ошибка при обработке запроса: {str(e)}"
                        },
                        "finish_reason": "error",
                        "index": 0
                    }
                ]
            }

    def call_with_structured_output(self, prompt: str, data: Dict[str, Any], result_schema: Type[BaseModel]) -> Dict[str, Any]:
        """
        Вызов модели с ожиданием структурированного вывода в соответствии с заданной схемой.
        
        Args:
            prompt: Промпт с инструкциями для модели.
            data: Данные для заполнения промпта.
            result_schema: Схема ожидаемого результата.
            
        Returns:
            Dict[str, Any]: Структурированный результат работы модели.
        """
        max_attempts = 3
        base_delay = 2
        
        for attempt in range(max_attempts):
            try:
                # Заполняем промпт данными
                filled_prompt = prompt.format(**data)
                
                # Создаем structured_llm с использованием схемы Pydantic
                structured_llm = self.giga.with_structured_output(result_schema)
                
                logger.info(f"Вызов GigaChat со структурированным выводом (попытка {attempt+1}/{max_attempts})")
                
                # Вызываем модель и получаем структурированный ответ
                result = structured_llm.invoke(filled_prompt)
                
                # Преобразуем Pydantic-объект в словарь
                result_dict = result.model_dump()
                
                logger.info("Успешно получен структурированный ответ")
                return result_dict
                
            except Exception as e:
                logger.error(f"Ошибка при вызове модели со структурированным выводом (попытка {attempt+1}/{max_attempts}): {e}")
                
                if attempt < max_attempts - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Повторная попытка через {delay} секунд...")
                    import time
                    time.sleep(delay)
        
        logger.error(f"Все {max_attempts} попытки вызова модели завершились неудачно")
        
        # Возвращаем пустой шаблон результата с дефолтными значениями
        default_result = {}
        for field_name, field in result_schema.model_fields.items():
            if field.is_required():
                if "float" in str(field.annotation).lower():
                    default_result[field_name] = 0.0
                elif "int" in str(field.annotation).lower():
                    default_result[field_name] = 0
                elif "str" in str(field.annotation).lower():
                    default_result[field_name] = "Не удалось получить данные"
                elif "List" in str(field.annotation):
                    default_result[field_name] = []
                elif "Dict" in str(field.annotation):
                    default_result[field_name] = {}
                else:
                    default_result[field_name] = None
        
        # Если это анализ требований, добавляем специфичные поля
        if "total_score" in default_result:
            default_result["total_score"] = 0.0
            default_result["clarity_score"] = 0.0
            default_result["completeness_score"] = 0.0
            default_result["consistency_score"] = 0.0
            default_result["testability_score"] = 0.0
            default_result["feasibility_score"] = 0.0
            default_result["problematic_requirements"] = []
            default_result["missing_aspects"] = []
            default_result["improvement_suggestions"] = []
            default_result["overall_assessment"] = "Не удалось выполнить анализ требований. Пожалуйста, попробуйте еще раз."
        
        return default_result 