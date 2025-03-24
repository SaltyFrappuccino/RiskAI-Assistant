"""
Основной модуль FastAPI приложения для анализа кода.
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from models.data_models import AnalysisRequest, AnalysisResult
from agents.analyzer import CodeAnalyzer
from utils.logging_config import setup_logging
import config

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="RiskAI Assistant",
    description="API для анализа кода с использованием LangChain и GigaChat",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание анализатора кода
code_analyzer = CodeAnalyzer()


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
        
        # Логирование параметров запроса
        logger.info("Story: %s", request.story[:100] + "..." if request.story and len(request.story) > 100 else request.story)
        logger.info("Requirements: %s", request.requirements[:100] + "..." if request.requirements and len(request.requirements) > 100 else "Не предоставлены")
        logger.info("Code: %s", request.code[:100] + "..." if request.code and len(request.code) > 100 else "Не предоставлен")
        logger.info("Test cases: %s", request.test_cases[:100] + "..." if request.test_cases and len(request.test_cases) > 100 else "Не предоставлены")
        
        # Выполнение анализа кода
        result = code_analyzer.analyze(request)
        
        logger.info("Анализ кода успешно выполнен")
        return result
    except Exception as e:
        logger.error(f"Ошибка при анализе кода: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при анализе кода: {str(e)}",
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