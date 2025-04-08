import axios from 'axios';

const API_URL = 'http://localhost:8080';

/**
 * Отправка запроса на анализ кода
 * @param {Object} data - данные для анализа
 * @param {string} data.story - краткое описание задачи
 * @param {string} data.requirements - требования к продукту
 * @param {string} data.code - код, реализующий задачу
 * @param {string} data.test_cases - тест-кейсы для проверки кода
 * @param {boolean} data.enable_preprocessing - включение предобработки текста
 * @param {boolean} data.extreme_mode - режим экстремальной обработки текста
 * @param {boolean} data.use_cache - использование кэша для ускорения анализа
 * @returns {Promise} результат анализа
 */
export const analyzeCode = async (data) => {
  try {
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
 * @param {boolean} data.use_cache - использование кэша для ускорения анализа
 * @returns {Promise} обработанные данные
 */
export const preprocessData = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/preprocess`, data);
    return response.data;
  } catch (error) {
    console.error('Ошибка при предобработке данных:', error);
    return data;
  }
};

/**
 * Получение статистики использования кэша
 * @returns {Promise} статистика использования кэша
 */
export const getCacheStats = async () => {
  try {
    const response = await axios.get(`${API_URL}/cache/stats`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при получении статистики кэша:', error);
    throw error;
  }
};

/**
 * Очистка кэша
 * @returns {Promise} результат операции
 */
export const clearCache = async () => {
  try {
    const response = await axios.post(`${API_URL}/cache/clear`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при очистке кэша:', error);
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

export const analyzeRequirements = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/analyze_requirements`, data);
    return response.data;
  } catch (error) {
    console.error("Ошибка при анализе требований:", error);
    throw error;
  }
}; 

/**
 * Форматирование документа по шаблону/правилам
 * @param {Object} data - данные для форматирования
 * @param {string} data.template_rules - шаблон или правила форматирования
 * @param {string} data.document_content - содержимое документа для форматирования
 * @param {boolean} data.use_cache - использование кэша для ускорения форматирования
 * @returns {Promise} результат форматирования
 */
export const formatDocument = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/format_document`, data);
    return response.data;
  } catch (error) {
    console.error("Ошибка при форматировании документа:", error);
    throw error;
  }
};

/**
 * Продолжение диалога с форматировщиком документов
 * @param {Object} data - данные для продолжения форматирования
 * @param {string} data.user_message - сообщение пользователя
 * @param {string} data.template_rules - шаблон или правила форматирования
 * @param {string} data.document_content - содержимое документа для форматирования
 * @param {Array} data.conversation_history - история диалога
 * @param {boolean} data.use_cache - использование кэша для ускорения форматирования
 * @returns {Promise} обновленный результат форматирования
 */
export const continueFormatting = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/format_document/continue`, data);
    return response.data;
  } catch (error) {
    console.error("Ошибка при продолжении форматирования:", error);
    throw error;
  }
};