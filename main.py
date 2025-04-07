"""
Основной модуль FastAPI приложения для анализа кода.
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from models.data_models import AnalysisRequest, AnalysisResult, CacheStatistics, RequirementsAnalysisRequest, RequirementsAnalysisResult
from agents.analyzer import CodeAnalyzer
from agents.preprocessor_agent import PreprocessorAgent
from services.gigachat_service import GigaChatService
from services.cache_service import CacheService
from utils.logging_config import setup_logging
import config
from agents.requirements_analyzer_agent import RequirementsAnalyzerAgent

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RiskAI Assistant",
    description="API для анализа кода с использованием LangChain и GigaChat",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gigachat_service = GigaChatService()
cache_service = CacheService()

code_analyzer = CodeAnalyzer(cache_service=cache_service)

preprocessor = PreprocessorAgent(gigachat_service)

# Руководства Сбера по написанию требований
sber_guidelines = """
Общий набор правил для описания требований в Confluence (Сбер)
Структурировано, детально, с акцентом на однозначность, проверяемость и удобство совместной работы.

1. Общие принципы написания требований
Избегайте неоднозначности:

Не используйте слова: «примерно», «возможно», «в будущем», «и так далее».

Заменяйте на конкретику: «в течение 2 секунд», «на основе данных из системы X».

Ссылайтесь на источники:

Указывайте документы, регламенты, письма или решения, на которых основано требование (например: «Согласно ТЗ версии 2.3 от 12.05.2024»).

Используйте глоссарий:

Все термины, аббревиатуры (даже очевидные, как «СБП» или «КИС») должны быть расшифрованы в глоссарии страницы/раздела.

Формулируйте требования через «Должно»:

Неправильно: «Система может проверять данные».

Правильно: «Система должна проверять данные на соответствие шаблону X перед сохранением».

2. Структура документа
Используйте шаблоны:

Для каждого типа документа (Юзер-Кейс, Бизнес-требование, API-спецификация) создавайте отдельные шаблоны с обязательными разделами.

Оглавление и якоря:

Добавляйте оглавление через макрос Confluence. Для длинных страниц используйте якорные ссылки.

Версионность:

Фиксируйте версии документа в заголовке (например: «Версия 1.2 от 20.05.2024»), а изменения описывайте в разделе «История правок».

3. Детализация требований
Правило «5W+H»:

Каждое требование должно отвечать на:

What (Что должно быть сделано?),

Why (Зачем это нужно бизнесу/пользователю?),

Who (Кто исполнитель/ответственный?),

When (Сроки/триггеры выполнения?),

Where (Где это будет применяться?),

How (Как это будет работать?).

Разделяйте функциональные и нефункциональные требования:

Функциональные: «Пользователь должен иметь возможность скачать отчёт в PDF».

Нефункциональные: «Формирование PDF-отчёта должно занимать не более 5 секунд при нагрузке до 1000 пользователей».

Указывайте приоритеты:

Используйте метки: «Must Have», «Should Have», «Could Have» (MoSCoW-метод).

4. Визуализация и схемы
Используйте Draw.io для схем:

Все архитектурные и процессные схемы рисуйте в Draw.io с описанием элементов. Не прикрепляйте изображения без редактируемого исходника.

Варфреймы и макеты:

Добавляйте ссылки на Figma/Sketch с версиями. Для статичных изображений указывайте: «Макет утверждён UX-командой 15.05.2024».

Таблицы для БД:

Описывайте поля в формате:

Название поля	Тип	Описание	Ограничения
user_id	UUID	Уникальный ID	NOT NULL, PK

5. API-спецификации
Шаблон для методов API:

Указывайте:

Endpoint, HTTP-метод,

Headers (например, Authorization: Bearer <token>),

Request/Response-примеры в JSON/XML,

Коды ошибок и их описание.

6. Юзер-Кейсы и сценарии
Структура юзер-кейса:

Предусловия: Что должно быть выполнено до начала сценария.

Основной поток: Шаги по порядку (например: «1. Пользователь нажимает кнопку "Отправить"»).

Альтернативные потоки: Обработка ошибок, исключения.

Постусловия: Состояние системы после выполнения.

Используйте таблицы для сценариев:

Шаг	Действие	Ожидаемый результат
1	Нажать "Добавить карту"	Открывается форма ввода данных
2	Ввести номер карты	Поле валидируется (16 цифр)

7. Работа с данными
Описание источников данных:

Для каждого поля/данного указывайте:

Откуда берётся (например, «Справочник банковских отделений (система ABC)»),

Частоту обновления (ежедневно/в реальном времени),

Ответственного за актуальность.

Маски и валидация:

Чётко прописывайте форматы:

«Телефон: 10 цифр, шаблон +7 (XXX) XXX-XX-XX»,

«Пароль: минимум 8 символов, буквы и цифры».

8. Совместная работа и ревью
Тегирование и ответственные:

На каждой странице указывайте:

@Ответственный_аналитик,

#проект_Платежи,

#статус_черновик.

Комментарии и обсуждения:

Все спорные моменты фиксируйте через макрос «Комментарий» в Confluence. Не используйте личные сообщения для согласования.

Ревью требований:

Перед утверждением проводите ревью с участием: аналитика, разработчика, тестировщика, бизнес-представителя.

9. Проверка качества
Критерии качества требований:

Требование считается корректным, если оно:

Специфично (чётко сформулировано),

Измеримо (есть критерии успеха),

Достижимо (в рамках ресурсов),

Актуально (соответствует целям проекта),

Ограничено по времени (дедлайны/этапы).

Чек-лист перед публикацией:

Нет противоречий с другими требованиями,

Есть ссылки на источники,

Указаны приоритеты,

Визуализация добавлена и подписана.

10. Интеграция с другими системами
Ссылки на задачи:

Для каждой функциональности указывайте задачу в Jira (например: PROJ-123). Используйте макрос «Jira Issues».

Привязка к тест-кейсам:

Требование должно иметь ссылку на тест-кейс в TestRail или аналогичной системе.

11. Безопасность и нормативы
Упоминание НСИ и стандартов:

Например: «Данные шифруются по стандарту ГОСТ Р 34.12-2015» или «Согласовано с отделом безопасности (протокол №X от 01.06.2024)».

Права доступа:

В Confluence настройте права так, чтобы конфиденциальные данные были доступны только утверждённым участникам.
"""

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalysisRequest):
    """
    Анализ кода с использованием LangChain и GigaChat.
    
    Args:
        request: Запрос на анализ кода.
        
    Returns:
        AnalysisResult: Результат анализа кода.
    """
    try:
        logger.info("Получен запрос на анализ кода")
        
        logger.info("Story: %s", request.story[:100] + "..." if request.story and len(request.story) > 100 else request.story)
        logger.info("Requirements: %s", request.requirements[:100] + "..." if request.requirements and len(request.requirements) > 100 else "Не предоставлены")
        logger.info("Code: %s", request.code[:100] + "..." if request.code and len(request.code) > 100 else "Не предоставлен")
        logger.info("Test cases: %s", request.test_cases[:100] + "..." if request.test_cases and len(request.test_cases) > 100 else "Не предоставлены")
        logger.info("Enable preprocessing: %s", "Включено" if request.enable_preprocessing else "Выключено")
        logger.info("Use cache: %s", "Включено" if request.use_cache else "Выключено")
        
        if request.enable_preprocessing:
            logger.info("Extreme mode: %s", "Включен" if request.extreme_mode else "Выключен")
        
        if request.enable_preprocessing:
            logger.info("Предобработка данных перед анализом")
            processed_data = await preprocess_data(request)
        else:
            logger.info("Предобработка данных отключена, используем исходные данные")
            processed_data = {
                "story": request.story or "",
                "requirements": request.requirements or "",
                "code": request.code or "",
                "test_cases": request.test_cases or "",
                "extreme_mode": False 
            }
        
        processed_data["use_cache"] = request.use_cache
        
        result = code_analyzer.analyze(processed_data)
        
        if request.enable_preprocessing:
            result.processed_data = processed_data
        else:
            result.processed_data = {
                "preprocessing_disabled": True,
                "message": "Предобработка данных была отключена"
            }
        
        if request.use_cache:
            result.cache_stats = cache_service.get_cache_statistics()
            logger.info(f"Статистика кэширования: {result.cache_stats.cache_usage_summary}")
            
            if result.cache_stats.cache_hits > 0:
                logger.info(f"Найдено в кэше: {result.cache_stats.cache_hits} элемент(ов)")
                if result.cache_stats.cached_bugs:
                    logger.info(f"Найденные в кэше баги: {', '.join(result.cache_stats.cached_bugs)}")
                if result.cache_stats.cached_vulnerabilities:
                    logger.info(f"Найденные в кэше уязвимости: {', '.join(result.cache_stats.cached_vulnerabilities)}")
                if result.cache_stats.cached_recommendations:
                    logger.info(f"Найденные в кэше рекомендации: {', '.join(result.cache_stats.cached_recommendations)}")
            
            if result.cache_stats.cache_saves > 0:
                logger.info(f"Добавлено в кэш: {result.cache_stats.cache_saves} элемент(ов)")
        
        logger.info("Анализ кода успешно выполнен")
        return result
    except Exception as e:
        logger.error(f"Ошибка при анализе кода: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при анализе кода: {str(e)}",
        )


@app.post("/preprocess")
async def preprocess_data(request: AnalysisRequest):
    """
    Предобработка данных перед анализом.
    
    Args:
        request: Запрос на предобработку данных.
        
    Returns:
        dict: Предобработанные данные.
    """
    try:
        logger.info("Получен запрос на предобработку данных")
        logger.info("Extreme mode: %s", "Включен" if request.extreme_mode else "Выключен")
        
        data = {
            "story": request.story or "",
            "requirements": request.requirements or "",
            "code": request.code or "",
            "test_cases": request.test_cases or "",
            "extreme_mode": request.extreme_mode or False
        }
        
        processed_data = preprocessor.analyze(data)
        
        logger.info("Предобработка данных успешно выполнена")
        return processed_data
    except Exception as e:
        logger.error(f"Ошибка при предобработке данных: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при предобработке данных: {str(e)}",
        )


@app.get("/cache/stats", response_model=CacheStatistics)
async def get_cache_stats():
    """
    Получение статистики использования кэша.
    
    Returns:
        CacheStatistics: Статистика использования кэша.
    """
    logger.info("Запрос на получение статистики кэша")
    try:
        stats = cache_service.get_cache_statistics()
        return stats
    except Exception as e:
        logger.error(f"Ошибка при получении статистики кэша: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении статистики кэша: {str(e)}",
        )


@app.post("/cache/clear")
async def clear_cache():
    """
    Очистка кэша.
    
    Returns:
        dict: Результат операции.
    """
    logger.info("Запрос на очистку кэша")
    try:
        cache_service.clear_cache()
        return {"status": "ok", "message": "Кэш успешно очищен"}
    except Exception as e:
        logger.error(f"Ошибка при очистке кэша: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при очистке кэша: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """
    Проверка работоспособности API.
    
    Returns:
        dict: Статус API.
    """
    logger.info("Запрос на проверку работоспособности API")
    return {"status": "ok"}


@app.post("/analyze_requirements", response_model=RequirementsAnalysisResult)
async def analyze_requirements(request: RequirementsAnalysisRequest):
    """
    Анализирует требования на их состоятельность и компетентность.

    Args:
        request: Запрос на анализ требований с требованиями и опциональными руководствами.

    Returns:
        RequirementsAnalysisResult: Результат анализа требований.
    """
    logger.info("Получен запрос на анализ требований")

    try:
        # Использование кэша, если включено
        if request.use_cache and cache_service:
            # TODO: Реализовать кэширование результатов анализа требований
            pass

        if not request.requirements:
            logger.warning("Требования не предоставлены")
            raise HTTPException(
                status_code=400, 
                detail="Необходимо предоставить требования для анализа"
            )

        # Создаем сервис GigaChat
        gigachat_service = GigaChatService()
        
        # Создаем агента для анализа требований
        requirements_analyzer = RequirementsAnalyzerAgent(gigachat_service)
        
        # Вызываем анализ требований
        result = requirements_analyzer.analyze({
            "requirements": request.requirements,
            "guidelines": request.guidelines or sber_guidelines,
        })
        
        # Преобразуем результат в модель ответа
        
        # Обработка problematic_requirements - преобразование строк в словари
        problematic_requirements = result.get("problematic_requirements", [])
        processed_problematic_requirements = []
        
        for requirement in problematic_requirements:
            # Если это строка, преобразуем в словарь
            if isinstance(requirement, str):
                req_dict = {
                    "requirement": requirement,
                    "description": "Проблема с требованием",
                    "severity": "medium",
                    "type": "Проблема"
                }
                processed_problematic_requirements.append(req_dict)
            else:
                # Если это уже словарь, просто добавляем
                processed_problematic_requirements.append(requirement)
        
        requirements_analysis_result = RequirementsAnalysisResult(
            total_score=result.get("total_score", 0.0),
            clarity_score=result.get("clarity_score", 0.0),
            completeness_score=result.get("completeness_score", 0.0),
            consistency_score=result.get("consistency_score", 0.0),
            testability_score=result.get("testability_score", 0.0),
            feasibility_score=result.get("feasibility_score", 0.0),
            problematic_requirements=processed_problematic_requirements,
            missing_aspects=result.get("missing_aspects", []),
            improvement_suggestions=result.get("improvement_suggestions", []),
            overall_assessment=result.get("overall_assessment", ""),
        )

        logger.info("Анализ требований успешно выполнен")
        return requirements_analysis_result

    except Exception as e:
        logger.error(f"Ошибка при анализе требований: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Произошла ошибка при анализе требований: {str(e)}"
        )


if __name__ == "__main__":
    port = config.PORT
    logger.info(f"Запуск сервера на порту {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 