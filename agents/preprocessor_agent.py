"""
Модуль содержит агента для предварительной обработки текста.
"""
import logging

from services.gigachat_service import GigaChatService
from agents.base_agent import CodeAnalysisAgent
import prompts.preprocessor_agent
import config

logger = logging.getLogger(__name__)


class PreprocessorAgent(CodeAnalysisAgent):
    """
    Агент для предварительной обработки текста требований, кода и тест-кейсов.
    
    Этот агент улучшает форматирование текста и может сокращать его для более
    эффективного анализа другими агентами.
    """
    
    def __init__(self, gigachat_service: GigaChatService):
        """
        Инициализация агента.
        
        Args:
            gigachat_service: Сервис для взаимодействия с GigaChat.
        """
        super().__init__(
            gigachat_service=gigachat_service, 
            prompt=prompts.preprocessor_agent.normal_prompt
        )
    
    def analyze(self, data):
        """
        Выполнение предобработки данных.
        
        Args:
            data: Данные для обработки, содержащие story, requirements, code, test_cases и extreme_mode.
            
        Returns:
            dict: Обработанные данные.
        """
        logger.info(f"Запуск {self.__class__.__name__} в режиме {'экстремальный' if data.get('extreme_mode') else 'обычный'}")
        
        if data.get('extreme_mode'):
            self.prompt = prompts.preprocessor_agent.extreme_prompt
        else:
            self.prompt = prompts.preprocessor_agent.normal_prompt
        
        story = data.get('story', '')
        requirements = data.get('requirements', '')
        code = data.get('code', '')
        test_cases = data.get('test_cases', '')
        
        processed_data = {
            'story': story,
            'requirements': requirements,
            'code': code,
            'test_cases': test_cases
        }
        
        if story.strip():
            processed_data['story'] = self._process_text('story', story)
            
        if requirements.strip():
            processed_data['requirements'] = self._process_text('requirements', requirements)
            
        if code.strip():
            processed_data['code'] = self._process_text('code', code)
            
        if test_cases.strip():
            processed_data['test_cases'] = self._process_text('test_cases', test_cases)
        
        processed_data['extreme_mode'] = data.get('extreme_mode', False)
        
        logger.info(f"Агент {self.__class__.__name__} завершил работу")
        return processed_data
    
    def _process_text(self, field_name, text):
        """
        Обработка конкретного текстового поля.
        
        Args:
            field_name: Название поля (story, requirements, code, test_cases).
            text: Текст для обработки.
            
        Returns:
            str: Обработанный текст.
        """
        try:
            logger.info(f"Обработка поля {field_name}")
            
            data = {
                'text': text,
                'field_type': field_name
            }
            
            response = self.gigachat_service.call_agent_with_prompt(self.prompt, data)
            
            if isinstance(response, str):
                processed_text = response
            elif isinstance(response, dict):
                if 'error' in response:
                    logger.error(f"Ошибка обработки {field_name}: {response['error']}")
                    return text
                processed_text = response.get('text', text)
            else:
                logger.warning(f"Неожиданный тип ответа от GigaChat: {type(response)}. Используем исходный текст.")
                return text
            
            logger.info(f"Поле {field_name} успешно обработано")
            return processed_text
        except Exception as e:
            logger.error(f"Ошибка при обработке поля {field_name}: {e}")
            return text 