"""
Модуль содержит модели данных для приложения.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """
    Модель запроса для анализа кода.
    """
    story: Optional[str] = Field(None, description="Краткое описание задачи")
    requirements: Optional[str] = Field(None, description="Требования к продукту")
    code: Optional[str] = Field(None, description="Код, реализующий задачу")
    test_cases: Optional[str] = Field(None, description="Тест-кейсы для проверки кода")
    extreme_mode: Optional[bool] = Field(False, description="Режим экстремальной обработки текста")


class Bug(BaseModel):
    """
    Модель для представления обнаруженного бага.
    """
    description: str = Field(..., description="Описание бага")
    code_snippet: str = Field(..., description="Фрагмент кода, где обнаружен баг")
    severity: str = Field(..., description="Серьезность бага (критический, высокий, средний, низкий)")
    fix: Optional[str] = Field(None, description="Предлагаемое исправление бага")


class Vulnerability(BaseModel):
    """
    Модель для представления обнаруженной уязвимости.
    """
    description: str = Field(..., description="Описание уязвимости")
    code_snippet: str = Field(..., description="Фрагмент кода, где обнаружена уязвимость")
    severity: str = Field(..., description="Серьезность уязвимости (критическая, высокая, средняя, низкая)")
    mitigation: str = Field(..., description="Рекомендации по устранению уязвимости")
    attack_vectors: Optional[str] = Field(None, description="Возможные сценарии атак")
    potential_impact: Optional[str] = Field(None, description="Потенциальные последствия уязвимости")


class Recommendation(BaseModel):
    """
    Модель для представления рекомендации по улучшению кода.
    """
    description: str = Field(..., description="Описание рекомендации")
    code_snippet: str = Field(..., description="Фрагмент кода, к которому относится рекомендация")
    improved_code: Optional[str] = Field(None, description="Улучшенный вариант кода")
    reason: Optional[str] = Field(None, description="Причина, почему рекомендация важна")


class Metrics(BaseModel):
    """
    Модель для представления метрик анализа.
    """
    code_requirements_match: float = Field(..., description="Процент соответствия кода требованиям")
    test_requirements_match: float = Field(..., description="Процент соответствия тест-кейсов требованиям")
    test_code_match: float = Field(..., description="Процент соответствия тест-кейсов коду")


class AnalysisResult(BaseModel):
    """
    Модель для представления результата анализа.
    """
    metrics: Metrics = Field(..., description="Метрики анализа")
    bugs: List[Bug] = Field(default_factory=list, description="Обнаруженные баги")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Обнаруженные уязвимости")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Рекомендации по улучшению кода")
    summary: str = Field(..., description="Общее заключение по результатам анализа")
    satisfied_requirements: List[str] = Field(default_factory=list, description="Список выполненных требований")
    unsatisfied_requirements: List[str] = Field(default_factory=list, description="Список невыполненных требований")
    metrics_explanation: Optional[str] = Field(None, description="Подробное объяснение метрик")
    requirements_details: Optional[str] = Field(None, description="Подробная информация о выполненных и невыполненных требованиях")
    test_coverage_details: Optional[str] = Field(None, description="Подробная информация о покрытии кода тестами")
    processed_data: Optional[Dict[str, Any]] = Field(None, description="Данные после предобработки") 