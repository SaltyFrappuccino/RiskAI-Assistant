"""
Модуль для кэширования результатов анализа кода.
"""
import os
import json
import time
import logging
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
import pickle
from pathlib import Path

from models.data_models import (
    Bug, Vulnerability, Recommendation, CacheStatistics, CachedItem,
    CachedBug, CachedVulnerability, CachedRecommendation, CachedRequirement
)

# Настройка логирования
logger = logging.getLogger(__name__)


class CacheService:
    """
    Сервис для кэширования результатов анализа кода.
    """

    def __init__(self, cache_dir: str = "cache", ttl_days: int = 30):
        """
        Инициализация сервиса кэширования.
        
        Args:
            cache_dir: Директория для хранения кэша.
            ttl_days: Время жизни элементов кэша в днях.
        """
        self.cache_dir = cache_dir
        self.ttl_days = ttl_days
        self.stats = CacheStatistics()
        
        # Создание директорий для кэша
        self._create_cache_dirs()
        
        # Загрузка кэша из файлов
        self.bugs_cache: Dict[str, CachedBug] = {}
        self.vulnerabilities_cache: Dict[str, CachedVulnerability] = {}
        self.recommendations_cache: Dict[str, CachedRecommendation] = {}
        self.requirements_cache: Dict[str, CachedRequirement] = {}
        
        self._load_cache()
        
        # Очистка устаревших записей в кэше
        self._clean_expired_items()
        
        logger.info(f"Сервис кэширования инициализирован. Директория кэша: {cache_dir}")

    def _create_cache_dirs(self):
        """
        Создание директорий для хранения кэша.
        """
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "bugs"), exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "vulnerabilities"), exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "recommendations"), exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "requirements"), exist_ok=True)

    def _load_cache(self):
        """
        Загрузка кэша из файлов.
        """
        try:
            self._load_cache_type("bugs", self.bugs_cache, CachedBug)
            self._load_cache_type("vulnerabilities", self.vulnerabilities_cache, CachedVulnerability)
            self._load_cache_type("recommendations", self.recommendations_cache, CachedRecommendation)
            self._load_cache_type("requirements", self.requirements_cache, CachedRequirement)
        except Exception as e:
            logger.error(f"Ошибка при загрузке кэша: {e}")

    def _load_cache_type(self, cache_type: str, cache_dict: Dict, model_class: Any):
        """
        Загрузка конкретного типа кэша из файлов.
        
        Args:
            cache_type: Тип кэша (bugs, vulnerabilities, recommendations, requirements).
            cache_dict: Словарь для хранения загруженных данных.
            model_class: Класс модели для десериализации.
        """
        cache_path = os.path.join(self.cache_dir, cache_type)
        files = [f for f in os.listdir(cache_path) if f.endswith('.pkl')]
        
        for file in files:
            try:
                file_path = os.path.join(cache_path, file)
                with open(file_path, 'rb') as f:
                    cached_item = pickle.load(f)
                    
                # Проверка типа и валидности
                if isinstance(cached_item, model_class):
                    cache_dict[cached_item.item_id] = cached_item
                else:
                    logger.warning(f"Неверный тип элемента кэша в файле {file_path}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке файла кэша {file}: {e}")

    def _clean_expired_items(self):
        """
        Очистка устаревших записей в кэше.
        """
        expiry_date = datetime.now() - timedelta(days=self.ttl_days)
        
        self._clean_expired_items_type(self.bugs_cache, "bugs", expiry_date)
        self._clean_expired_items_type(self.vulnerabilities_cache, "vulnerabilities", expiry_date)
        self._clean_expired_items_type(self.recommendations_cache, "recommendations", expiry_date)
        self._clean_expired_items_type(self.requirements_cache, "requirements", expiry_date)

    def _clean_expired_items_type(self, cache_dict: Dict[str, CachedItem], cache_type: str, expiry_date: datetime):
        """
        Очистка устаревших записей в кэше конкретного типа.
        
        Args:
            cache_dict: Словарь кэша.
            cache_type: Тип кэша (bugs, vulnerabilities, recommendations, requirements).
            expiry_date: Дата истечения срока действия.
        """
        expired_keys = []
        for key, item in cache_dict.items():
            if item.last_used < expiry_date:
                expired_keys.append(key)
                
                # Удаление файла
                file_path = os.path.join(self.cache_dir, cache_type, f"{key}.pkl")
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла кэша {file_path}: {e}")
        
        # Удаление ключей из словаря
        for key in expired_keys:
            del cache_dict[key]
            
        logger.info(f"Удалено {len(expired_keys)} устаревших записей из кэша {cache_type}")

    def _compute_hash(self, data: str) -> str:
        """
        Вычисление хэша строки.
        
        Args:
            data: Строка для хэширования.
            
        Returns:
            str: Хэш строки.
        """
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def _compute_similarity_hash(self, code: str) -> str:
        """
        Вычисление хэша для определения схожести кода.
        Удаляет комментарии, лишние пробелы и переносы строк для более точного сравнения.
        
        Args:
            code: Код для хэширования.
            
        Returns:
            str: Хэш кода.
        """
        # Очистка кода от несущественных элементов
        # Это упрощенная реализация, для разных языков может потребоваться доработка
        cleaned_code = code.strip()
        
        # Удаление многострочных комментариев
        cleaned_code = self._remove_multiline_comments(cleaned_code)
        
        # Удаление однострочных комментариев
        cleaned_code = self._remove_singleline_comments(cleaned_code)
        
        # Удаление лишних пробелов и переносов строк
        cleaned_code = ' '.join(cleaned_code.split())
        
        return self._compute_hash(cleaned_code)

    def _remove_multiline_comments(self, code: str) -> str:
        """
        Удаление многострочных комментариев из кода.
        
        Args:
            code: Исходный код.
            
        Returns:
            str: Код без многострочных комментариев.
        """
        # Простая реализация для типичных комментариев /* ... */
        # Для разных языков может потребоваться доработка
        result = code
        while "/*" in result and "*/" in result:
            start = result.find("/*")
            end = result.find("*/", start) + 2
            if start != -1 and end != 1:
                result = result[:start] + " " + result[end:]
            else:
                break
        return result

    def _remove_singleline_comments(self, code: str) -> str:
        """
        Удаление однострочных комментариев из кода.
        
        Args:
            code: Исходный код.
            
        Returns:
            str: Код без однострочных комментариев.
        """
        # Простая реализация для типичных комментариев // и #
        # Для разных языков может потребоваться доработка
        result = []
        for line in code.split('\n'):
            # Проверка на // комментарии
            if "//" in line:
                line = line.split("//")[0]
            # Проверка на # комментарии
            if "#" in line:
                line = line.split("#")[0]
            result.append(line)
        return '\n'.join(result)

    def find_cached_bugs(self, code: str) -> Tuple[List[Bug], List[str]]:
        """
        Поиск закэшированных багов для данного кода.
        
        Args:
            code: Код для анализа.
            
        Returns:
            Tuple[List[Bug], List[str]]: Найденные в кэше баги и их идентификаторы.
        """
        code_hash = self._compute_similarity_hash(code)
        found_bugs = []
        bug_ids = []
        
        for bug_id, cached_bug in self.bugs_cache.items():
            # Поиск по хэшу или частичному совпадению кода
            if cached_bug.content_hash == code_hash or cached_bug.related_code_pattern in code:
                cached_bug.last_used = datetime.now()
                cached_bug.use_count += 1
                
                # Создаем копию бага с меткой из кэша
                bug_copy = Bug(
                    description=cached_bug.bug_data.description,
                    code_snippet=cached_bug.bug_data.code_snippet,
                    severity=cached_bug.bug_data.severity,
                    fix=cached_bug.bug_data.fix,
                    from_cache=True
                )
                
                found_bugs.append(bug_copy)
                bug_ids.append(bug_id)
                
                # Обновляем статистику
                self.stats.cache_hits += 1
                
                # Сохраняем обновленный элемент кэша
                self._save_cached_item(cached_bug, "bugs")
                
                logger.info(f"Найден баг в кэше: {bug_id}")
        
        # Если ничего не найдено, увеличиваем счетчик промахов
        if not found_bugs:
            self.stats.cache_misses += 1
        
        # Добавляем найденные идентификаторы в статистику
        self.stats.cached_bugs.extend(bug_ids)
        
        return found_bugs, bug_ids

    def find_cached_vulnerabilities(self, code: str) -> Tuple[List[Vulnerability], List[str]]:
        """
        Поиск закэшированных уязвимостей для данного кода.
        
        Args:
            code: Код для анализа.
            
        Returns:
            Tuple[List[Vulnerability], List[str]]: Найденные в кэше уязвимости и их идентификаторы.
        """
        code_hash = self._compute_similarity_hash(code)
        found_vulnerabilities = []
        vulnerability_ids = []
        
        for vuln_id, cached_vuln in self.vulnerabilities_cache.items():
            # Поиск по хэшу или частичному совпадению кода
            if cached_vuln.content_hash == code_hash or cached_vuln.related_code_pattern in code:
                cached_vuln.last_used = datetime.now()
                cached_vuln.use_count += 1
                
                # Создаем копию уязвимости с меткой из кэша
                vuln_copy = Vulnerability(
                    description=cached_vuln.vulnerability_data.description,
                    code_snippet=cached_vuln.vulnerability_data.code_snippet,
                    severity=cached_vuln.vulnerability_data.severity,
                    mitigation=cached_vuln.vulnerability_data.mitigation,
                    attack_vectors=cached_vuln.vulnerability_data.attack_vectors,
                    potential_impact=cached_vuln.vulnerability_data.potential_impact,
                    from_cache=True
                )
                
                found_vulnerabilities.append(vuln_copy)
                vulnerability_ids.append(vuln_id)
                
                # Обновляем статистику
                self.stats.cache_hits += 1
                
                # Сохраняем обновленный элемент кэша
                self._save_cached_item(cached_vuln, "vulnerabilities")
                
                logger.info(f"Найдена уязвимость в кэше: {vuln_id}")
        
        # Если ничего не найдено, увеличиваем счетчик промахов
        if not found_vulnerabilities:
            self.stats.cache_misses += 1
        
        # Добавляем найденные идентификаторы в статистику
        self.stats.cached_vulnerabilities.extend(vulnerability_ids)
        
        return found_vulnerabilities, vulnerability_ids

    def find_cached_recommendations(self, code: str) -> Tuple[List[Recommendation], List[str]]:
        """
        Поиск закэшированных рекомендаций для данного кода.
        
        Args:
            code: Код для анализа.
            
        Returns:
            Tuple[List[Recommendation], List[str]]: Найденные в кэше рекомендации и их идентификаторы.
        """
        code_hash = self._compute_similarity_hash(code)
        found_recommendations = []
        recommendation_ids = []
        
        for rec_id, cached_rec in self.recommendations_cache.items():
            # Поиск по хэшу или частичному совпадению кода
            if cached_rec.content_hash == code_hash or cached_rec.related_code_pattern in code:
                cached_rec.last_used = datetime.now()
                cached_rec.use_count += 1
                
                # Создаем копию рекомендации с меткой из кэша
                rec_copy = Recommendation(
                    description=cached_rec.recommendation_data.description,
                    code_snippet=cached_rec.recommendation_data.code_snippet,
                    improved_code=cached_rec.recommendation_data.improved_code,
                    reason=cached_rec.recommendation_data.reason,
                    from_cache=True
                )
                
                found_recommendations.append(rec_copy)
                recommendation_ids.append(rec_id)
                
                # Обновляем статистику
                self.stats.cache_hits += 1
                
                # Сохраняем обновленный элемент кэша
                self._save_cached_item(cached_rec, "recommendations")
                
                logger.info(f"Найдена рекомендация в кэше: {rec_id}")
        
        # Если ничего не найдено, увеличиваем счетчик промахов
        if not found_recommendations:
            self.stats.cache_misses += 1
        
        # Добавляем найденные идентификаторы в статистику
        self.stats.cached_recommendations.extend(recommendation_ids)
        
        return found_recommendations, recommendation_ids

    def add_bug_to_cache(self, bug: Bug, code: str) -> str:
        """
        Добавление бага в кэш.
        
        Args:
            bug: Объект бага.
            code: Связанный код.
            
        Returns:
            str: Идентификатор кэшированного бага.
        """
        # Генерация уникального идентификатора
        bug_hash = self._compute_hash(bug.description + bug.code_snippet)
        bug_id = f"bug_{bug_hash}"
        
        # Проверка наличия в кэше
        if bug_id in self.bugs_cache:
            return bug_id
        
        # Определение паттерна кода
        code_pattern = bug.code_snippet
        
        # Создание кэшированного объекта
        cached_bug = CachedBug(
            item_id=bug_id,
            content_hash=self._compute_similarity_hash(code),
            bug_data=bug,
            related_code_pattern=code_pattern,
            tags=set(["bug", bug.severity])
        )
        
        # Добавление в кэш
        self.bugs_cache[bug_id] = cached_bug
        
        # Сохранение в файл
        self._save_cached_item(cached_bug, "bugs")
        
        # Обновление статистики
        self.stats.cache_saves += 1
        
        logger.info(f"Баг добавлен в кэш: {bug_id}")
        
        return bug_id

    def add_vulnerability_to_cache(self, vulnerability: Vulnerability, code: str) -> str:
        """
        Добавление уязвимости в кэш.
        
        Args:
            vulnerability: Объект уязвимости.
            code: Связанный код.
            
        Returns:
            str: Идентификатор кэшированной уязвимости.
        """
        # Генерация уникального идентификатора
        vuln_hash = self._compute_hash(vulnerability.description + vulnerability.code_snippet)
        vuln_id = f"vuln_{vuln_hash}"
        
        # Проверка наличия в кэше
        if vuln_id in self.vulnerabilities_cache:
            return vuln_id
        
        # Определение паттерна кода
        code_pattern = vulnerability.code_snippet
        
        # Создание кэшированного объекта
        cached_vuln = CachedVulnerability(
            item_id=vuln_id,
            content_hash=self._compute_similarity_hash(code),
            vulnerability_data=vulnerability,
            related_code_pattern=code_pattern,
            tags=set(["vulnerability", vulnerability.severity])
        )
        
        # Добавление в кэш
        self.vulnerabilities_cache[vuln_id] = cached_vuln
        
        # Сохранение в файл
        self._save_cached_item(cached_vuln, "vulnerabilities")
        
        # Обновление статистики
        self.stats.cache_saves += 1
        
        logger.info(f"Уязвимость добавлена в кэш: {vuln_id}")
        
        return vuln_id

    def add_recommendation_to_cache(self, recommendation: Recommendation, code: str) -> str:
        """
        Добавление рекомендации в кэш.
        
        Args:
            recommendation: Объект рекомендации.
            code: Связанный код.
            
        Returns:
            str: Идентификатор кэшированной рекомендации.
        """
        # Генерация уникального идентификатора
        rec_hash = self._compute_hash(recommendation.description + recommendation.code_snippet)
        rec_id = f"rec_{rec_hash}"
        
        # Проверка наличия в кэше
        if rec_id in self.recommendations_cache:
            return rec_id
        
        # Определение паттерна кода
        code_pattern = recommendation.code_snippet
        
        # Создание кэшированного объекта
        cached_rec = CachedRecommendation(
            item_id=rec_id,
            content_hash=self._compute_similarity_hash(code),
            recommendation_data=recommendation,
            related_code_pattern=code_pattern,
            tags=set(["recommendation"])
        )
        
        # Добавление в кэш
        self.recommendations_cache[rec_id] = cached_rec
        
        # Сохранение в файл
        self._save_cached_item(cached_rec, "recommendations")
        
        # Обновление статистики
        self.stats.cache_saves += 1
        
        logger.info(f"Рекомендация добавлена в кэш: {rec_id}")
        
        return rec_id

    def add_requirement_to_cache(self, requirement: str, satisfied: bool, code: Optional[str] = None) -> str:
        """
        Добавление требования в кэш.
        
        Args:
            requirement: Текст требования.
            satisfied: Статус выполнения требования.
            code: Связанный код (опционально).
            
        Returns:
            str: Идентификатор кэшированного требования.
        """
        # Генерация уникального идентификатора
        req_hash = self._compute_hash(requirement)
        req_id = f"req_{req_hash}"
        
        # Проверка наличия в кэше
        if req_id in self.requirements_cache:
            return req_id
        
        # Определение паттерна кода, если он предоставлен
        code_pattern = None
        content_hash = self._compute_hash(requirement)
        if code:
            code_pattern = code
            content_hash = self._compute_similarity_hash(code)
        
        # Создание кэшированного объекта
        cached_req = CachedRequirement(
            item_id=req_id,
            content_hash=content_hash,
            requirement_text=requirement,
            satisfied=satisfied,
            related_code_pattern=code_pattern,
            tags=set(["requirement", "satisfied" if satisfied else "unsatisfied"])
        )
        
        # Добавление в кэш
        self.requirements_cache[req_id] = cached_req
        
        # Сохранение в файл
        self._save_cached_item(cached_req, "requirements")
        
        # Обновление статистики
        self.stats.cache_saves += 1
        
        logger.info(f"Требование добавлено в кэш: {req_id}")
        
        return req_id

    def _save_cached_item(self, item: CachedItem, item_type: str):
        """
        Сохранение элемента кэша в файл.
        
        Args:
            item: Элемент кэша.
            item_type: Тип элемента кэша.
        """
        file_path = os.path.join(self.cache_dir, item_type, f"{item.item_id}.pkl")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(item, f)
            logger.debug(f"Элемент кэша сохранен: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении элемента кэша {item.item_id}: {e}")

    def get_cache_statistics(self) -> CacheStatistics:
        """
        Получение статистики использования кэша.
        
        Returns:
            CacheStatistics: Статистика использования кэша.
        """
        # Обновление сводной информации
        total_requests = self.stats.cache_hits + self.stats.cache_misses
        hit_rate = (self.stats.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        self.stats.cache_usage_summary = (
            f"Количество запросов: {total_requests}, "
            f"Использовано из кэша: {self.stats.cache_hits}, "
            f"Не найдено в кэше: {self.stats.cache_misses}, "
            f"Добавлено в кэш: {self.stats.cache_saves}, "
            f"Процент попаданий: {hit_rate:.2f}%"
        )
        
        return self.stats

    def reset_statistics(self):
        """
        Сброс статистики использования кэша.
        """
        self.stats = CacheStatistics()
        logger.info("Статистика использования кэша сброшена")

    def clear_cache(self):
        """
        Полная очистка кэша.
        """
        # Очистка словарей
        self.bugs_cache.clear()
        self.vulnerabilities_cache.clear()
        self.recommendations_cache.clear()
        self.requirements_cache.clear()
        
        # Очистка файлов
        cache_types = ["bugs", "vulnerabilities", "recommendations", "requirements"]
        for cache_type in cache_types:
            cache_path = os.path.join(self.cache_dir, cache_type)
            for file in os.listdir(cache_path):
                if file.endswith('.pkl'):
                    try:
                        os.remove(os.path.join(cache_path, file))
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла кэша {file}: {e}")
        
        logger.info("Кэш полностью очищен")
        
        # Сброс статистики
        self.reset_statistics() 