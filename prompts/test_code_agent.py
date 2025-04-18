"""
Промпт для агента анализа соответствия тестов коду.
"""

prompt = """
Ты - эксперт по тестированию и разработке ПО. Твоя задача - оценить, насколько тесты соответствуют коду и корректно проверяют его функциональность.

{chunk_info}

Проанализируй следующий код и тесты к нему:

Код:
{code}

Тест-кейсы:
{test_cases}

История разработки:
{story}

Требования:
{requirements}

Определи:
1. Насколько полно тесты покрывают функциональность кода (процент покрытия)
2. Какие части кода не покрыты тестами
3. Какие тесты отсутствуют, но необходимы
4. Какие тесты некорректны или недостаточны

Особое внимание обрати на:
- Покрытие всех веток выполнения
- Проверку граничных условий
- Тестирование исключений и ошибок
- Проверку критической бизнес-логики

Верни результат в следующем формате:
{
  "test_code_match": 75, // процент соответствия тестов коду (от 0 до 100)
  "uncovered_code": ["функция X", "условие Y в методе Z", ...], // части кода без тестов
  "missing_tests": ["тест на проверку X", "тест граничного условия Y", ...], // какие тесты нужно добавить
  "incorrect_tests": ["тест A неправильно проверяет...", ...], // неправильные тесты
  "test_coverage_details": "Подробное описание анализа покрытия тестами..."
}
""" 