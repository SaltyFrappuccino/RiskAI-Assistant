# RiskAI Assistant

Приложение для анализа кода с использованием LangChain и GigaChat.

## Описание

RiskAI Assistant - это инструмент для анализа кода, который проверяет:
- Соответствие кода требованиям
- Соответствие тест-кейсов требованиям
- Соответствие тест-кейсов коду
- Соответствие кода лучшим практикам
- Наличие потенциальных багов
- Наличие уязвимостей

Результатом анализа является подробный отчет с метриками, списком обнаруженных проблем и рекомендациями по улучшению кода.

## Установка и запуск

1. Склонируйте репозиторий:
```
git clone https://github.com/yourusername/RiskAI-Assistant.git
cd RiskAI-Assistant
```

2. Установите зависимости:
```
pip install -r requirements.txt
```

3. Настройте переменные окружения:
Создайте файл `.env` со следующим содержимым:
```
AUTH_KEY=your_gigachat_auth_key
AUTH_URL=
GIGA_URL=
PORT=8080
MODEL=GigaChat-2-Pro
```

4. Запустите приложение:
```
python main.py
```

API будет доступен по адресу: http://localhost:8080

## API

### POST /analyze

Анализ кода на соответствие требованиям.

**Запрос:**
```json
{
  "story": "Краткое описание задачи",
  "requirements": "Требования к продукту",
  "code": "Код, реализующий задачу",
  "test_cases": "Тест-кейсы для проверки кода"
}
```

**Ответ:**
```json
{
  "metrics": {
    "code_requirements_match": 85,
    "test_requirements_match": 75,
    "test_code_match": 80
  },
  "bugs": [
    {
      "description": "Описание бага",
      "code_snippet": "Фрагмент кода с багом",
      "severity": "критический"
    }
  ],
  "vulnerabilities": [
    {
      "description": "Описание уязвимости",
      "code_snippet": "Фрагмент кода с уязвимостью",
      "severity": "высокая",
      "mitigation": "Рекомендации по устранению"
    }
  ],
  "recommendations": [
    {
      "description": "Описание рекомендации",
      "code_snippet": "Фрагмент кода",
      "improved_code": "Улучшенный вариант кода"
    }
  ],
  "summary": "Общее заключение о качестве кода"
}
```

### GET /health

Проверка работоспособности API.

**Ответ:**
```json
{
  "status": "ok"
}
```

## Настройка промптов

Все промпты для агентов находятся в директории `prompts/`. Вы можете редактировать их для настройки поведения агентов.

## Зависимости

- FastAPI
- Uvicorn
- Pydantic
- LangChain
- GigaChat API 