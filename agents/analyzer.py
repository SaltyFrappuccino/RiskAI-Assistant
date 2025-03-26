"""
Модуль содержит основной класс для анализа кода с использованием агентов.
"""
import logging
from typing import Dict, Any, Optional, Union

from models.data_models import AnalysisRequest, AnalysisResult, Metrics
from services.gigachat_service import GigaChatService
from agents.code_requirements_agent import CodeRequirementsAgent
from agents.test_requirements_agent import TestRequirementsAgent
from agents.test_code_agent import TestCodeAgent
from agents.best_practices_agent import BestPracticesAgent
from agents.bug_detector_agent import BugDetectorAgent
from agents.vulnerability_detector_agent import VulnerabilityDetectorAgent
from agents.final_report_agent import FinalReportAgent
import config

# Настройка логирования
logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Класс для анализа кода с использованием агентов.
    """

    def __init__(self):
        """
        Инициализация анализатора кода.
        """
        logger.info("Инициализация CodeAnalyzer")
        self.gigachat_service = GigaChatService()
        self._init_agents()
    
    def _init_agents(self):
        """
        Инициализация агентов.
        """
        logger.info("Инициализация агентов")
        self.code_requirements_agent = CodeRequirementsAgent(self.gigachat_service)
        self.test_requirements_agent = TestRequirementsAgent(self.gigachat_service)
        self.test_code_agent = TestCodeAgent(self.gigachat_service)
        self.best_practices_agent = BestPracticesAgent(self.gigachat_service)
        self.bug_detector_agent = BugDetectorAgent(self.gigachat_service)
        self.vulnerability_detector_agent = VulnerabilityDetectorAgent(self.gigachat_service)
        self.final_report_agent = FinalReportAgent(self.gigachat_service)
        logger.info("Агенты успешно инициализированы")

    def analyze(self, request: Union[AnalysisRequest, Dict[str, Any]]) -> AnalysisResult:
        """
        Анализ кода с использованием агентов.
        
        Args:
            request: Запрос на анализ кода (объект AnalysisRequest или словарь).
            
        Returns:
            AnalysisResult: Результат анализа кода.
        """
        logger.info("Начало анализа кода")
        
        # Подготовка данных для анализа
        if isinstance(request, dict):
            # Если запрос - словарь (например, из preprocessor)
            data = {
                "story": request.get("story") or config.DEFAULT_STORY,
                "requirements": request.get("requirements") or config.DEFAULT_REQUIREMENTS,
                "code": request.get("code") or config.DEFAULT_CODE,
                "test_cases": request.get("test_cases") or config.DEFAULT_TEST_CASES,
            }
        else:
            # Если запрос - объект AnalysisRequest
            data = {
                "story": request.story or config.DEFAULT_STORY,
                "requirements": request.requirements or config.DEFAULT_REQUIREMENTS,
                "code": request.code or config.DEFAULT_CODE,
                "test_cases": request.test_cases or config.DEFAULT_TEST_CASES,
            }
        
        # Выполнение анализа с помощью агентов
        logger.info("Запуск агента проверки соответствия кода требованиям")
        code_requirements_result = self.code_requirements_agent.analyze(data)
        
        logger.info("Запуск агента проверки соответствия тест-кейсов требованиям")
        test_requirements_result = self.test_requirements_agent.analyze(data)
        
        logger.info("Запуск агента проверки соответствия тест-кейсов коду")
        test_code_result = self.test_code_agent.analyze(data)
        
        logger.info("Запуск агента проверки кода на соответствие лучшим практикам")
        best_practices_result = self.best_practices_agent.analyze(data)
        
        logger.info("Запуск агента обнаружения багов")
        bug_detector_result = self.bug_detector_agent.analyze(data)
        
        logger.info("Запуск агента обнаружения уязвимостей")
        vulnerability_detector_result = self.vulnerability_detector_agent.analyze(data)
        
        # Сбор результатов анализа для формирования итогового отчета
        report_data = {
            "code_requirements_result": code_requirements_result,
            "test_requirements_result": test_requirements_result,
            "test_code_result": test_code_result,
            "best_practices_result": best_practices_result,
            "bug_detector_result": bug_detector_result,
            "vulnerability_detector_result": vulnerability_detector_result,
        }
        
        # Формирование итогового отчета
        logger.info("Запуск агента формирования итогового отчета")
        final_report = self.final_report_agent.analyze(report_data)
        
        # Преобразование отчета в модель AnalysisResult
        try:
            logger.info("Формирование итогового результата анализа")
            
            # Убедимся, что метрики присутствуют и являются числами
            metrics = final_report.get("metrics", {})
            
            # Проверяем наличие и тип метрик, устанавливаем значения по умолчанию, если необходимо
            code_req_match = self._get_float_value(metrics.get("code_requirements_match"), 0.0)
            test_req_match = self._get_float_value(metrics.get("test_requirements_match"), 0.0)
            test_code_match = self._get_float_value(metrics.get("test_code_match"), 0.0)
            
            result = AnalysisResult(
                metrics=Metrics(
                    code_requirements_match=code_req_match,
                    test_requirements_match=test_req_match,
                    test_code_match=test_code_match,
                ),
                bugs=final_report.get("bugs", []),
                vulnerabilities=final_report.get("vulnerabilities", []),
                recommendations=final_report.get("recommendations", []),
                summary=final_report.get("summary", "Не удалось сформировать итоговый отчет"),
                satisfied_requirements=final_report.get("satisfied_requirements", []),
                unsatisfied_requirements=final_report.get("unsatisfied_requirements", []),
                metrics_explanation=metrics.get("metrics_explanation", ""),
                requirements_details=metrics.get("requirements_details", ""),
                test_coverage_details=metrics.get("test_coverage_details", ""),
            )
            logger.info("Анализ кода успешно завершен")
            return result
        except Exception as e:
            logger.error(f"Ошибка при формировании итогового результата: {e}")
            # Создание результата с ошибкой
            return AnalysisResult(
                metrics=Metrics(code_requirements_match=0.0, test_requirements_match=0.0, test_code_match=0.0),
                summary=f"Ошибка при формировании отчета: {str(e)}",
            )
    
    def _get_float_value(self, value, default: float = 0.0) -> float:
        """
        Безопасное получение float значения из переменной.
        
        Args:
            value: Значение для преобразования.
            default: Значение по умолчанию, если преобразование невозможно.
            
        Returns:
            float: Преобразованное значение или значение по умолчанию.
        """
        if value is None:
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Не удалось преобразовать {value} в float. Использовано значение по умолчанию {default}.")
            return default 