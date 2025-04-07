"""
Модуль содержит модели данных для приложения.
"""
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
from datetime import datetime
from models.agent_schemas import ProblematicRequirement


class AnalysisRequest(BaseModel):
    """
    Модель запроса для анализа кода.
    """
    story: Optional[str] = Field(None, description="Краткое описание задачи")
    requirements: Optional[str] = Field(None, description="Требования к продукту")
    code: Optional[str] = Field(None, description="Код, реализующий задачу")
    test_cases: Optional[str] = Field(None, description="Тест-кейсы для проверки кода")
    enable_preprocessing: Optional[bool] = Field(True, description="Включить предобработку текста")
    extreme_mode: Optional[bool] = Field(False, description="Режим экстремальной обработки текста")
    use_cache: Optional[bool] = Field(True, description="Использовать кэш для ускорения анализа")


class Bug(BaseModel):
    """
    Модель для представления обнаруженного бага.
    """
    description: str = Field(..., description="Описание бага")
    code_snippet: str = Field(..., description="Фрагмент кода, где обнаружен баг")
    severity: str = Field(..., description="Серьезность бага (критический, высокий, средний, низкий)")
    fix: Optional[str] = Field(None, description="Предлагаемое исправление бага")
    from_cache: Optional[bool] = Field(False, description="Получено из кэша")


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
    from_cache: Optional[bool] = Field(False, description="Получено из кэша")


class Recommendation(BaseModel):
    """
    Модель для представления рекомендации по улучшению кода.
    """
    description: str = Field(..., description="Описание рекомендации")
    code_snippet: str = Field(..., description="Фрагмент кода, к которому относится рекомендация")
    improved_code: Optional[str] = Field(None, description="Улучшенный вариант кода")
    reason: Optional[str] = Field(None, description="Причина, почему рекомендация важна")
    from_cache: Optional[bool] = Field(False, description="Получено из кэша")


class Metrics(BaseModel):
    """
    Модель для представления метрик анализа.
    """
    code_requirements_match: float = Field(..., description="Процент соответствия кода требованиям")
    test_requirements_match: float = Field(..., description="Процент соответствия тест-кейсов требованиям")
    test_code_match: float = Field(..., description="Процент соответствия тест-кейсов коду")


class CacheStatistics(BaseModel):
    """
    Модель для статистики использования кэша.
    """
    cache_hits: int = Field(0, description="Количество использований данных из кэша")
    cache_misses: int = Field(0, description="Количество запросов, не найденных в кэше")
    cache_saves: int = Field(0, description="Количество новых записей, добавленных в кэш")
    cache_usage_summary: Optional[str] = Field(None, description="Сводная информация об использовании кэша")
    cached_bugs: List[str] = Field(default_factory=list, description="Идентификаторы найденных в кэше багов")
    cached_vulnerabilities: List[str] = Field(default_factory=list, description="Идентификаторы найденных в кэше уязвимостей")
    cached_recommendations: List[str] = Field(default_factory=list, description="Идентификаторы найденных в кэше рекомендаций")


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
    cache_stats: Optional[CacheStatistics] = Field(None, description="Статистика использования кэша")


class CachedItem(BaseModel):
    """
    Базовая модель для кэшированных элементов.
    """
    item_id: str = Field(..., description="Уникальный идентификатор элемента")
    content_hash: str = Field(..., description="Хэш содержимого для быстрого сравнения")
    creation_date: datetime = Field(default_factory=datetime.now, description="Дата создания записи в кэше")
    last_used: datetime = Field(default_factory=datetime.now, description="Дата последнего использования")
    use_count: int = Field(1, description="Счетчик использований")
    tags: Set[str] = Field(default_factory=set, description="Теги для категоризации и поиска")


class CachedBug(CachedItem):
    """
    Модель для кэширования обнаруженного бага.
    """
    bug_data: Bug = Field(..., description="Данные обнаруженного бага")
    related_code_pattern: str = Field(..., description="Паттерн кода, связанный с багом")


class CachedVulnerability(CachedItem):
    """
    Модель для кэширования обнаруженной уязвимости.
    """
    vulnerability_data: Vulnerability = Field(..., description="Данные обнаруженной уязвимости")
    related_code_pattern: str = Field(..., description="Паттерн кода, связанный с уязвимостью")


class CachedRecommendation(CachedItem):
    """
    Модель для кэширования рекомендации по улучшению кода.
    """
    recommendation_data: Recommendation = Field(..., description="Данные рекомендации")
    related_code_pattern: str = Field(..., description="Паттерн кода, связанный с рекомендацией")


class CachedRequirement(CachedItem):
    """
    Модель для кэширования требования.
    """
    requirement_text: str = Field(..., description="Текст требования")
    satisfied: bool = Field(..., description="Статус выполнения требования")
    related_code_pattern: Optional[str] = Field(None, description="Связанный паттерн кода, если есть")


class RequirementsAnalysisRequest(BaseModel):
    """
    Модель запроса для анализа требований.
    """
    requirements: str = Field(..., description="Требования для анализа")
    guidelines: Optional[str] = Field(None, description="Руководства и стандарты для анализа требований")
    use_cache: Optional[bool] = Field(True, description="Использовать кэш для ускорения анализа")


class RequirementsAnalysisResult(BaseModel):
    """
    Модель для представления результата анализа требований.
    """
    total_score: float = Field(..., description="Общий балл качества требований")
    clarity_score: float = Field(..., description="Оценка ясности и конкретности требований")
    completeness_score: float = Field(..., description="Оценка полноты требований")
    consistency_score: float = Field(..., description="Оценка непротиворечивости требований")
    testability_score: float = Field(..., description="Оценка проверяемости требований")
    feasibility_score: float = Field(..., description="Оценка реализуемости требований")
    problematic_requirements: List[ProblematicRequirement] = Field(default_factory=list, description="Список проблемных требований с указанием проблем")
    missing_aspects: List[str] = Field(default_factory=list, description="Список аспектов, которые не покрыты требованиями")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Список предложений по улучшению требований")
    overall_assessment: str = Field(..., description="Общая оценка и заключение о качестве требований")
    cache_stats: Optional[CacheStatistics] = Field(None, description="Статистика использования кэша") 