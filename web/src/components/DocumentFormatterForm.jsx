import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Grid,
  Button,
  FormControlLabel,
  Switch,
  Divider,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';

/**
 * Форма для ввода шаблона/правил и документа для форматирования
 * @param {Object} props - свойства компонента
 * @param {Function} props.onFormatterSubmit - обработчик отправки формы
 * @param {boolean} props.loading - индикатор загрузки
 * @param {boolean} props.disabled - флаг отключения формы
 */
const DocumentFormatterForm = ({ onFormatterSubmit, loading, disabled }) => {
  const theme = useTheme();
  
  const [templateRules, setTemplateRules] = useState('');
  const [documentContent, setDocumentContent] = useState('');
  const [useCache, setUseCache] = useState(true);
  
  // Состояние для модального окна с примерами
  const [examplesOpen, setExamplesOpen] = useState(false);
  
  /**
   * Обработчик отправки формы
   * @param {Event} e - событие формы
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!templateRules.trim() || !documentContent.trim()) {
      return;
    }
    
    onFormatterSubmit({
      template_rules: templateRules,
      document_content: documentContent,
      use_cache: useCache
    });
  };
  
  /**
   * Обработчик открытия модального окна с примерами
   */
  const handleExamplesOpen = () => {
    setExamplesOpen(true);
  };
  
  /**
   * Обработчик закрытия модального окна с примерами
   */
  const handleExamplesClose = () => {
    setExamplesOpen(false);
  };
  
  /**
   * Обработчик выбора примера
   * @param {Object} example - выбранный пример
   */
  const selectExample = (example) => {
    setTemplateRules(example.template);
    setDocumentContent(example.document);
    setExamplesOpen(false);
  };
  
  // Примеры шаблонов и документов
  const examples = [
    {
      name: "Пример требований Сбера",
      template: `Правила для описания требований в Confluence (Сбербанк)

1. Структура документа должна включать:
- Заголовок с версией и датой (Версия X.Y от ДД.ММ.ГГГГ)
- Раздел "Общая информация" с кратким описанием продукта
- Раздел "Функциональные требования"
- Раздел "Нефункциональные требования"
- Раздел "История изменений"

2. Каждое требование должно:
- Начинаться с "Система должна..."
- Быть уникальным и иметь идентификатор REQ-XXX
- Содержать информацию о приоритете (Must Have, Should Have, Could Have)`,
      document: `Требования к Мобильному приложению

Мобильное приложение для заказа такси должно позволять пользователям вызывать такси, отслеживать поездку и оплачивать услуги.

Функциональные возможности:
- Регистрация пользователя
- Выбор адреса назначения
- Выбор типа автомобиля
- Оплата поездки
- Оценка водителя

Нефункциональные требования:
- Простота использования
- Безопасность данных
- Скорость работы`
    },
    {
      name: "Описание API",
      template: `Шаблон для документации REST API:

1. Каждый эндпоинт должен содержать:
   - HTTP метод (GET, POST, PUT, DELETE)
   - URL путь
   - Описание функциональности
   - Параметры запроса (query, path, body)
   - Ответы с кодами статуса
   - Примеры запросов и ответов в формате JSON

2. Структура документа:
   - Заголовок API
   - Базовый URL
   - Аутентификация
   - Список всех эндпоинтов, сгруппированных по ресурсам`,
      document: `Документация по API для работы с пользователями

API для управления пользователями системы поддерживает создание, получение, обновление и удаление данных пользователей.

Эндпоинты:
- Получение списка пользователей: GET /users
- Получение информации о пользователе: GET /users/{id}
- Создание пользователя: POST /users
- Обновление пользователя: PUT /users/{id}
- Удаление пользователя: DELETE /users/{id}

Пример запроса:
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "role": "admin"
}`
    }
  ];
  
  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            Форматирование документа по шаблону
          </Typography>
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={handleExamplesOpen}
            disabled={disabled || loading}
          >
            Примеры
          </Button>
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Укажите шаблон или набор правил для форматирования документа и содержимое документа, 
          которое нужно отформатировать согласно этим правилам.
        </Typography>
        
        <Divider sx={{ mb: 3 }} />
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" component="h3" sx={{ mb: 2 }}>
              Шаблон / Правила
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={15}
              label="Введите шаблон или правила форматирования"
              value={templateRules}
              onChange={(e) => setTemplateRules(e.target.value)}
              disabled={disabled || loading}
              sx={{ mb: 2 }}
              InputProps={{
                sx: {
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                }
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h6" component="h3" sx={{ mb: 2 }}>
              Документ для форматирования
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={15}
              label="Введите содержимое документа"
              value={documentContent}
              onChange={(e) => setDocumentContent(e.target.value)}
              disabled={disabled || loading}
              sx={{ mb: 2 }}
              InputProps={{
                sx: {
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                }
              }}
            />
          </Grid>
        </Grid>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
          <FormControlLabel
            control={
              <Switch 
                checked={useCache} 
                onChange={(e) => setUseCache(e.target.checked)}
                disabled={disabled || loading}
                color="primary"
              />
            }
            label="Использовать кэш"
          />
          
          <Button 
            type="submit" 
            variant="contained" 
            color="primary" 
            disabled={disabled || loading || !templateRules.trim() || !documentContent.trim()}
            sx={{ minWidth: 150 }}
          >
            {loading ? <CircularProgress size={24} /> : "Форматировать"}
          </Button>
        </Box>
      </form>
      
      {/* Модальное окно с примерами */}
      <Dialog open={examplesOpen} onClose={handleExamplesClose} maxWidth="md" fullWidth>
        <DialogTitle>Примеры шаблонов и документов</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2}>
            {examples.map((example, index) => (
              <Grid item xs={12} key={index}>
                <Paper 
                  elevation={1} 
                  sx={{ 
                    p: 2, 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover
                    }
                  }}
                  onClick={() => selectExample(example)}
                >
                  <Typography variant="h6" component="h3">
                    {example.name}
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2">Шаблон:</Typography>
                      <Typography 
                        variant="body2" 
                        component="div" 
                        sx={{ 
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'monospace',
                          fontSize: '0.8rem',
                          p: 1,
                          backgroundColor: theme.palette.background.paper,
                          maxHeight: 150,
                          overflow: 'auto'
                        }}
                      >
                        {example.template.substring(0, 200)}...
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2">Документ:</Typography>
                      <Typography 
                        variant="body2" 
                        component="div" 
                        sx={{ 
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'monospace',
                          fontSize: '0.8rem',
                          p: 1,
                          backgroundColor: theme.palette.background.paper,
                          maxHeight: 150,
                          overflow: 'auto'
                        }}
                      >
                        {example.document.substring(0, 200)}...
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleExamplesClose} color="primary">
            Закрыть
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default DocumentFormatterForm;