import axios from 'axios';

// Базовый URL API
const API_URL = 'http://localhost:8082';

/**
 * Отправка запроса на анализ кода
 * @param {Object} data - данные для анализа
 * @param {string} data.story - краткое описание задачи
 * @param {string} data.requirements - требования к продукту
 * @param {string} data.code - код, реализующий задачу
 * @param {string} data.test_cases - тест-кейсы для проверки кода
 * @returns {Promise} результат анализа
 */
export const analyzeCode = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/analyze`, data);
    return response.data;
  } catch (error) {
    console.error('Ошибка при отправке запроса на анализ:', error);
    throw error;
  }
};

/**
 * Проверка работоспособности API
 * @returns {Promise} статус API
 */
export const checkApiHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при проверке работоспособности API:', error);
    throw error;
  }
}; 