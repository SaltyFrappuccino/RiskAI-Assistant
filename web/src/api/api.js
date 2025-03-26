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
 * @param {boolean} data.enable_preprocessing - включение предобработки текста
 * @param {boolean} data.extreme_mode - режим экстремальной обработки текста
 * @returns {Promise} результат анализа
 */
export const analyzeCode = async (data) => {
  try {
    // Если предобработка включена, обрабатываем данные перед отправкой
    const dataToSend = data.enable_preprocessing 
      ? await preprocessData(data)
      : data;
      
    const response = await axios.post(`${API_URL}/analyze`, dataToSend);
    return response.data;
  } catch (error) {
    console.error('Ошибка при отправке запроса на анализ:', error);
    throw error;
  }
};

/**
 * Предобработка данных перед отправкой на анализ
 * @param {Object} data - данные для анализа
 * @param {string} data.story - краткое описание задачи
 * @param {string} data.requirements - требования к продукту
 * @param {string} data.code - код, реализующий задачу
 * @param {string} data.test_cases - тест-кейсы для проверки кода
 * @param {boolean} data.enable_preprocessing - включение предобработки текста
 * @param {boolean} data.extreme_mode - режим экстремальной обработки текста
 * @returns {Promise} обработанные данные
 */
export const preprocessData = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/preprocess`, data);
    return response.data;
  } catch (error) {
    console.error('Ошибка при предобработке данных:', error);
    // В случае ошибки используем оригинальные данные
    return data;
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