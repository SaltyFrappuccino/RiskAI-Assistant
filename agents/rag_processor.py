"""
Модуль содержит процессор для обработки больших текстов с использованием RAG.
"""
import logging
from typing import List, Dict, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.gigachat_service import GigaChatService

logger = logging.getLogger(__name__)

class RAGProcessor:
    """
    Процессор для обработки больших текстов с использованием RAG (Retrieval Augmented Generation).
    Разбивает большие тексты на части и анализирует их по отдельности.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация процессора RAG.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        self.gigachat_service = gigachat_service
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,  # Примерный размер чанка в символах
            chunk_overlap=500,  # Перекрытие между чанками
            length_function=len,
        )
    
    def process_large_text(self, text: str, chunk_size: int = 4000) -> List[str]:
        """
        Разбивает большой текст на части.
        
        Args:
            text: Исходный текст для разбиения.
            chunk_size: Максимальный размер чанка в символах.
            
        Returns:
            List[str]: Список частей текста.
        """
        if len(text) < chunk_size:
            return [text]
        
        # Обновляем размер чанка, если он отличается от дефолтного
        if chunk_size != 4000:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=min(500, chunk_size // 8),  # Адаптивное перекрытие
                length_function=len,
            )
        
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Текст разбит на {len(chunks)} частей")
        return chunks
    
    def analyze_with_rag(
        self,
        prompt_template: str,
        text: str,
        result_schema: Any,
        additional_data: Optional[Dict[str, Any]] = None,
        chunk_size: int = 4000
    ) -> Dict[str, Any]:
        """
        Анализирует большой текст с использованием RAG.
        
        Args:
            prompt_template: Шаблон промпта для анализа.
            text: Текст для анализа.
            result_schema: Схема результата.
            additional_data: Дополнительные данные для включения в промпт.
            chunk_size: Максимальный размер чанка в символах.
            
        Returns:
            Dict[str, Any]: Объединенный результат анализа всех частей.
        """
        if len(text) < chunk_size:
            # Если текст маленький, анализируем его целиком
            prompt_data = {"requirements": text}
            if additional_data:
                prompt_data.update(additional_data)
            
            return self.gigachat_service.call_with_structured_output(
                prompt=prompt_template,
                data=prompt_data,
                result_schema=result_schema
            )
        
        # Разбиваем текст на части
        chunks = self.process_large_text(text, chunk_size)
        
        # Анализируем каждую часть отдельно
        chunk_results = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Анализ части {i+1} из {len(chunks)}")
            
            prompt_data = {
                "requirements": chunk,
                "chunk_info": f"Это часть {i+1} из {len(chunks)} всего текста требований.",
                "is_chunk": True
            }
            
            if additional_data:
                prompt_data.update(additional_data)
            
            result = self.gigachat_service.call_with_structured_output(
                prompt=prompt_template,
                data=prompt_data,
                result_schema=result_schema
            )
            
            chunk_results.append(result)
        
        # Объединяем результаты всех частей
        return self._merge_results(chunk_results, result_schema)
    
    def _merge_results(self, results: List[Dict[str, Any]], schema_class: Any) -> Dict[str, Any]:
        """
        Объединяет результаты анализа отдельных частей.
        
        Args:
            results: Список результатов анализа отдельных частей.
            schema_class: Класс схемы результата.
            
        Returns:
            Dict[str, Any]: Объединенный результат.
        """
        if not results:
            return {}
        
        # Создаем пустой результат
        merged_result = {}
        
        # Обрабатываем каждое поле схемы отдельно
        for field_name, field in schema_class.model_fields.items():
            field_type = str(field.annotation).lower()
            
            # Обработка числовых полей (вычисляем среднее)
            if "float" in field_type or "int" in field_type:
                values = [result.get(field_name, 0) for result in results if field_name in result]
                if values:
                    merged_result[field_name] = sum(values) / len(values)
                else:
                    merged_result[field_name] = 0
            
            # Обработка строковых полей (объединяем с разделителем)
            elif "str" in field_type:
                values = [result.get(field_name, "") for result in results if field_name in result and result.get(field_name)]
                if field_name == "overall_assessment":
                    # Для общей оценки берем последнюю часть и добавляем примечание
                    if values:
                        merged_result[field_name] = values[-1] + "\n\nПримечание: Данная оценка основана на анализе нескольких частей требований."
                    else:
                        merged_result[field_name] = "Не удалось провести анализ."
                else:
                    # Для других строковых полей просто объединяем
                    merged_result[field_name] = "\n\n".join(values)
            
            # Обработка списков (объединяем списки)
            elif "list" in field_type:
                merged_list = []
                for result in results:
                    if field_name in result and result[field_name]:
                        merged_list.extend(result[field_name])
                merged_result[field_name] = merged_list
            
            # По умолчанию просто берем значение из первого результата
            else:
                for result in results:
                    if field_name in result:
                        merged_result[field_name] = result[field_name]
                        break
        
        logger.info(f"Объединены результаты анализа {len(results)} частей")
        return merged_result 