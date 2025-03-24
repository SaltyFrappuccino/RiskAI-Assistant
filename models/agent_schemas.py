"""
Модуль содержит схемы Pydantic для агентов, которые используются при работе с GigaChat.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class MissingRequirement(BaseModel):
    """
    Модель для представления требования, которое отсутствует в коде.
    """
    requirement: str = Field(..., description="Требование, которое отсутствует в коде")
    description: str = Field(..., description="Подробное описание несоответствия")


class IncorrectImplementation(BaseModel):
    """
    Модель для представления требования, которое реализовано некорректно.
    """
    requirement: str = Field(..., description="Требование, которое реализовано некорректно")
    code_snippet: str = Field(..., description="Фрагмент кода с проблемой")
    description: str = Field(..., description="Описание проблемы")


class CodeRequirementsResult(BaseModel):
    """
    Модель для результата анализа соответствия кода требованиям.
    """
    code_requirements_match: float = Field(..., description="Процент соответствия кода требованиям (от 0 до 100)")
    missing_requirements: List[MissingRequirement] = Field(default_factory=list, description="Список требований, которые отсутствуют в коде")
    incorrect_implementations: List[IncorrectImplementation] = Field(default_factory=list, description="Список требований, которые реализованы некорректно")


class MissingTestCase(BaseModel):
    """
    Модель для представления требования, для которого отсутствуют тест-кейсы.
    """
    requirement: str = Field(..., description="Требование, для которого отсутствуют тест-кейсы")
    description: str = Field(..., description="Подробное описание несоответствия")


class IncompleteTestCase(BaseModel):
    """
    Модель для представления требования, для которого тест-кейсы неполные.
    """
    requirement: str = Field(..., description="Требование, для которого тест-кейсы неполные")
    test_snippet: str = Field(..., description="Фрагмент тест-кейса")
    description: str = Field(..., description="Описание проблемы")


class TestRequirementsResult(BaseModel):
    """
    Модель для результата анализа соответствия тест-кейсов требованиям.
    """
    test_requirements_match: float = Field(..., description="Процент соответствия тест-кейсов требованиям (от 0 до 100)")
    missing_test_cases: List[MissingTestCase] = Field(default_factory=list, description="Список требований, для которых отсутствуют тест-кейсы")
    incomplete_test_cases: List[IncompleteTestCase] = Field(default_factory=list, description="Список требований, для которых тест-кейсы неполные")


class UntestedCode(BaseModel):
    """
    Модель для представления функции/метода, который не покрыт тестами.
    """
    function: str = Field(..., description="Функция/метод, который не покрыт тестами")
    description: str = Field(..., description="Подробное описание непокрытой функциональности")


class NonexistentFunctionalityTest(BaseModel):
    """
    Модель для представления тест-кейса, тестирующего несуществующую функциональность.
    """
    test: str = Field(..., description="Тест-кейс, тестирующий несуществующую функциональность")
    test_snippet: str = Field(..., description="Фрагмент тест-кейса")
    description: str = Field(..., description="Описание проблемы")


class IncorrectTest(BaseModel):
    """
    Модель для представления тест-кейса, некорректно тестирующего функциональность.
    """
    test: str = Field(..., description="Тест-кейс, некорректно тестирующий функциональность")
    test_snippet: str = Field(..., description="Фрагмент тест-кейса")
    description: str = Field(..., description="Описание проблемы")


class TestCodeResult(BaseModel):
    """
    Модель для результата анализа соответствия тест-кейсов коду.
    """
    test_code_match: float = Field(..., description="Процент соответствия тест-кейсов коду (от 0 до 100)")
    untested_code: List[UntestedCode] = Field(default_factory=list, description="Список функций/методов, для которых отсутствуют тест-кейсы")
    nonexistent_functionality_tests: List[NonexistentFunctionalityTest] = Field(default_factory=list, description="Список тест-кейсов, тестирующих несуществующую функциональность")
    incorrect_tests: List[IncorrectTest] = Field(default_factory=list, description="Список тест-кейсов, некорректно тестирующих функциональность")


class Recommendation(BaseModel):
    """
    Модель для представления рекомендации по улучшению кода.
    """
    description: str = Field(..., description="Подробное описание рекомендации")
    code_snippet: str = Field(..., description="Фрагмент кода с проблемой")
    improved_code: str = Field(..., description="Улучшенный вариант кода")
    reason: str = Field(..., description="Причина, почему рекомендация важна")


class BestPracticesResult(BaseModel):
    """
    Модель для результата анализа соответствия кода лучшим практикам.
    """
    recommendations: List[Recommendation] = Field(default_factory=list, description="Список рекомендаций по улучшению кода")


class Bug(BaseModel):
    """
    Модель для представления обнаруженного бага.
    """
    description: str = Field(..., description="Подробное описание бага")
    code_snippet: str = Field(..., description="Фрагмент кода с багом")
    severity: str = Field(..., description="Серьезность бага (критический, высокий, средний, низкий)")
    fix: str = Field(..., description="Предлагаемое исправление бага")


class BugDetectorResult(BaseModel):
    """
    Модель для результата анализа обнаружения багов.
    """
    bugs: List[Bug] = Field(default_factory=list, description="Список обнаруженных багов")


class Vulnerability(BaseModel):
    """
    Модель для представления обнаруженной уязвимости.
    """
    description: str = Field(..., description="Подробное описание уязвимости")
    code_snippet: str = Field(..., description="Фрагмент кода с уязвимостью")
    severity: str = Field(..., description="Серьезность уязвимости (критическая, высокая, средняя, низкая)")
    mitigation: str = Field(..., description="Рекомендации по устранению уязвимости")


class VulnerabilityDetectorResult(BaseModel):
    """
    Модель для результата анализа обнаружения уязвимостей.
    """
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Список обнаруженных уязвимостей")


class FinalReportMetrics(BaseModel):
    """
    Модель для представления метрик в итоговом отчете.
    """
    code_requirements_match: float = Field(..., description="Процент соответствия кода требованиям")
    test_requirements_match: float = Field(..., description="Процент соответствия тест-кейсов требованиям")
    test_code_match: float = Field(..., description="Процент соответствия тест-кейсов коду")
    bugs_count: int = Field(..., description="Количество обнаруженных багов")
    vulnerabilities_count: int = Field(..., description="Количество обнаруженных уязвимостей")
    recommendations_count: int = Field(..., description="Количество рекомендаций по улучшению кода")


class FinalReportResult(BaseModel):
    """
    Модель для результата итогового отчета.
    """
    metrics: FinalReportMetrics = Field(..., description="Метрики анализа")
    bugs: List[Bug] = Field(default_factory=list, description="Список обнаруженных багов")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Список обнаруженных уязвимостей")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Список рекомендаций по улучшению кода")
    summary: str = Field(..., description="Общее заключение о качестве кода и рекомендации по дальнейшим действиям") 