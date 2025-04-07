"""
Основной модуль FastAPI приложения для анализа кода.
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from models.data_models import AnalysisRequest, AnalysisResult, CacheStatistics
from agents.analyzer import CodeAnalyzer
from agents.preprocessor_agent import PreprocessorAgent
from services.gigachat_service import GigaChatService
from services.cache_service import CacheService
from utils.logging_config import setup_logging
import config

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


if __name__ == "__main__":
    port = config.PORT
    logger.info(f"Запуск сервера на порту {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 