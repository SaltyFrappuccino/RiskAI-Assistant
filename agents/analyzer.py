"""
Модуль содержит основной класс для анализа кода с использованием агентов.
"""
import logging
from typing import Dict, Any, Optional, Union, List

from models.data_models import AnalysisRequest, AnalysisResult, Metrics, Bug, Vulnerability, Recommendation
from services.gigachat_service import GigaChatService
from services.cache_service import CacheService
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

    def __init__(self, cache_service: Optional[CacheService] = None):
        """
        Инициализация анализатора кода.
        
        Args:
            cache_service: Сервис кэширования результатов анализа.
        """
        logger.info("Инициализация CodeAnalyzer")
        self.gigachat_service = GigaChatService()
        self.cache_service = cache_service
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
                "use_cache": request.get("use_cache", True)
            }
        else:
            # Если запрос - объект AnalysisRequest
            data = {
                "story": request.story or config.DEFAULT_STORY,
                "requirements": request.requirements or config.DEFAULT_REQUIREMENTS,
                "code": request.code or config.DEFAULT_CODE,
                "test_cases": request.test_cases or config.DEFAULT_TEST_CASES,
                "use_cache": request.use_cache if hasattr(request, 'use_cache') else True
            }
        
        # Проверяем, включен ли кэш и доступен ли сервис кэширования
        use_cache = data.get("use_cache", True) and self.cache_service is not None
        
        # Выполнение анализа с помощью агентов
        if use_cache:
            logger.info("Кэширование включено. Проверка наличия подобных результатов в кэше")
            # Проверка кэша для кода
            cached_bugs, bug_ids = self.cache_service.find_cached_bugs(data["code"])
            cached_vulnerabilities, vuln_ids = self.cache_service.find_cached_vulnerabilities(data["code"])
            cached_recommendations, rec_ids = self.cache_service.find_cached_recommendations(data["code"])
            
            if cached_bugs or cached_vulnerabilities or cached_recommendations:
                logger.info(f"Найдены похожие результаты в кэше: {len(cached_bugs)} багов, {len(cached_vulnerabilities)} уязвимостей, {len(cached_recommendations)} рекомендаций")
            else:
                logger.info("В кэше не найдено подходящих результатов")
        else:
            logger.info("Кэширование отключено или сервис кэширования недоступен")
            cached_bugs = []
            cached_vulnerabilities = []
            cached_recommendations = []
        
        # Выполнение анализа с помощью агентов
        logger.info("Запуск агента проверки соответствия кода требованиям")
        code_requirements_result = self.code_requirements_agent.analyze(data)
        
        logger.info("Запуск агента проверки соответствия тест-кейсов требованиям")
        test_requirements_result = self.test_requirements_agent.analyze(data)
        
        logger.info("Запуск агента проверки соответствия тест-кейсов коду")
        test_code_result = self.test_code_agent.analyze(data)
        
        logger.info("Запуск агента проверки кода на соответствие лучшим практикам")
        best_practices_result = self.best_practices_agent.analyze(data)
        
        # Если есть кэшированные результаты для багов, используем их
        if use_cache and cached_bugs:
            logger.info(f"Используем {len(cached_bugs)} кэшированных багов")
            # Интегрируем кэшированные баги в результат
            bug_detector_result = self.bug_detector_agent.analyze(data)
            bug_detector_result["bugs"] = self._merge_bugs(bug_detector_result.get("bugs", []), cached_bugs)
        else:
            logger.info("Запуск агента обнаружения багов")
            bug_detector_result = self.bug_detector_agent.analyze(data)
        
        # Если есть кэшированные результаты для уязвимостей, используем их
        if use_cache and cached_vulnerabilities:
            logger.info(f"Используем {len(cached_vulnerabilities)} кэшированных уязвимостей")
            # Интегрируем кэшированные уязвимости в результат
            vulnerability_detector_result = self.vulnerability_detector_agent.analyze(data)
            vulnerability_detector_result["vulnerabilities"] = self._merge_vulnerabilities(
                vulnerability_detector_result.get("vulnerabilities", []), 
                cached_vulnerabilities
            )
        else:
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
        
        # Если есть кэшированные рекомендации, добавляем их
        if use_cache and cached_recommendations:
            logger.info(f"Добавляем {len(cached_recommendations)} кэшированных рекомендаций")
            # Добавляем кэшированные рекомендации в отчет
            if "recommendations" not in report_data:
                report_data["recommendations"] = []
            report_data["recommendations"].extend(cached_recommendations)
        
        # Формирование итогового отчета
        logger.info("Запуск агента формирования итогового отчета")
        final_report = self.final_report_agent.analyze(report_data)
        
        # Добавляем новые результаты в кэш, если кэширование включено
        if use_cache and self.cache_service:
            self._add_results_to_cache(final_report, data["code"])
        
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
    
    def _merge_bugs(self, detected_bugs: List[Dict[str, Any]], cached_bugs: List[Bug]) -> List[Dict[str, Any]]:
        """
        Объединение обнаруженных и кэшированных багов.
        
        Args:
            detected_bugs: Список обнаруженных багов.
            cached_bugs: Список кэшированных багов.
            
        Returns:
            List[Dict[str, Any]]: Объединенный список багов.
        """
        # Преобразуем объекты Bug в словари для совместимости с форматом агента
        cached_bugs_dicts = [
            {
                "description": bug.description,
                "code_snippet": bug.code_snippet,
                "severity": bug.severity,
                "fix": bug.fix,
                "from_cache": True
            }
            for bug in cached_bugs
        ]
        
        # Объединяем списки
        return detected_bugs + cached_bugs_dicts
    
    def _merge_vulnerabilities(self, detected_vulns: List[Dict[str, Any]], cached_vulns: List[Vulnerability]) -> List[Dict[str, Any]]:
        """
        Объединение обнаруженных и кэшированных уязвимостей.
        
        Args:
            detected_vulns: Список обнаруженных уязвимостей.
            cached_vulns: Список кэшированных уязвимостей.
            
        Returns:
            List[Dict[str, Any]]: Объединенный список уязвимостей.
        """
        # Преобразуем объекты Vulnerability в словари для совместимости с форматом агента
        cached_vulns_dicts = [
            {
                "description": vuln.description,
                "code_snippet": vuln.code_snippet,
                "severity": vuln.severity,
                "mitigation": vuln.mitigation,
                "attack_vectors": vuln.attack_vectors,
                "potential_impact": vuln.potential_impact,
                "from_cache": True
            }
            for vuln in cached_vulns
        ]
        
        # Объединяем списки
        return detected_vulns + cached_vulns_dicts
    
    def _add_results_to_cache(self, final_report: Dict[str, Any], code: str):
        """
        Добавление результатов анализа в кэш.
        
        Args:
            final_report: Итоговый отчет.
            code: Исходный код.
        """
        try:
            # Добавление багов в кэш
            if "bugs" in final_report and final_report["bugs"]:
                for bug_data in final_report["bugs"]:
                    # Проверяем, что баг не из кэша
                    if not bug_data.get("from_cache", False):
                        bug = Bug(
                            description=bug_data["description"],
                            code_snippet=bug_data["code_snippet"],
                            severity=bug_data["severity"],
                            fix=bug_data.get("fix")
                        )
                        self.cache_service.add_bug_to_cache(bug, code)
                
                logger.info(f"Добавлено {len(final_report['bugs'])} багов в кэш")
            
            # Добавление уязвимостей в кэш
            if "vulnerabilities" in final_report and final_report["vulnerabilities"]:
                for vuln_data in final_report["vulnerabilities"]:
                    # Проверяем, что уязвимость не из кэша
                    if not vuln_data.get("from_cache", False):
                        vulnerability = Vulnerability(
                            description=vuln_data["description"],
                            code_snippet=vuln_data["code_snippet"],
                            severity=vuln_data["severity"],
                            mitigation=vuln_data["mitigation"],
                            attack_vectors=vuln_data.get("attack_vectors"),
                            potential_impact=vuln_data.get("potential_impact")
                        )
                        self.cache_service.add_vulnerability_to_cache(vulnerability, code)
                
                logger.info(f"Добавлено {len(final_report['vulnerabilities'])} уязвимостей в кэш")
            
            # Добавление рекомендаций в кэш
            if "recommendations" in final_report and final_report["recommendations"]:
                for rec_data in final_report["recommendations"]:
                    # Проверяем, что рекомендация не из кэша
                    if not rec_data.get("from_cache", False):
                        recommendation = Recommendation(
                            description=rec_data["description"],
                            code_snippet=rec_data["code_snippet"],
                            improved_code=rec_data.get("improved_code"),
                            reason=rec_data.get("reason")
                        )
                        self.cache_service.add_recommendation_to_cache(recommendation, code)
                
                logger.info(f"Добавлено {len(final_report['recommendations'])} рекомендаций в кэш")
            
            # Добавление требований в кэш
            if "satisfied_requirements" in final_report:
                for req in final_report["satisfied_requirements"]:
                    self.cache_service.add_requirement_to_cache(req, True, code)
            
            if "unsatisfied_requirements" in final_report:
                for req in final_report["unsatisfied_requirements"]:
                    self.cache_service.add_requirement_to_cache(req, False, code)
            
            logger.info("Результаты анализа успешно добавлены в кэш")
        except Exception as e:
            logger.error(f"Ошибка при добавлении результатов в кэш: {e}")
    
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