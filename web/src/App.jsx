import React, { useState, useEffect } from 'react';
import { 
  ThemeProvider, 
  CssBaseline, 
  Container, 
  Alert, 
  Snackbar, 
  Box, 
  Fade,
  Grow,
  CircularProgress
} from '@mui/material';
import theme from './styles/theme';
import Header from './components/Header';
import CodeForm from './components/CodeForm';
import ExamplesSelector from './components/ExamplesSelector';
import AnalysisReport from './components/AnalysisReport';
import { analyzeCode, checkApiHealth } from './api/api';
import './styles/globalStyles.css';

/**
 * Главный компонент приложения с современным дизайном и анимациями
 */
const App = () => {
  // Состояние для хранения результатов анализа
  const [analysisResult, setAnalysisResult] = useState(null);
  
  // Состояние для отображения загрузки
  const [loading, setLoading] = useState(false);
  
  // Состояние для отображения уведомлений
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Состояние для проверки работоспособности API
  const [apiStatus, setApiStatus] = useState({
    checked: false,
    isOnline: false,
    checking: true
  });

  // Состояние для хранения выбранного примера
  const [selectedExample, setSelectedExample] = useState(null);

  // Проверка работоспособности API при загрузке приложения
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await checkApiHealth();
        setApiStatus({
          checked: true,
          isOnline: response.status === 'ok',
          checking: false
        });
      } catch (error) {
        setApiStatus({
          checked: true,
          isOnline: false,
          checking: false
        });
        showNotification('API недоступен. Убедитесь, что сервер запущен на порту 8082.', 'error');
      }
    };

    checkApiStatus();
  }, []);

  // Функция для отображения уведомлений
  const showNotification = (message, severity = 'info') => {
    setNotification({
      open: true,
      message,
      severity
    });
  };

  // Обработчик закрытия уведомления
  const handleCloseNotification = () => {
    setNotification(prev => ({
      ...prev,
      open: false
    }));
  };

  // Обработчик выбора примера
  const handleExampleSelect = (example) => {
    setSelectedExample(example);
    showNotification(`Пример "${example.title}" загружен`, 'success');
  };

  // Обработчик отправки формы
  const handleAnalyzeSubmit = async (formData) => {
    // Проверка наличия данных
    if (!formData.code.trim()) {
      showNotification('Необходимо заполнить поле "Код" для анализа', 'warning');
      return;
    }

    setLoading(true);
    setAnalysisResult(null); // Сбрасываем предыдущий результат

    try {
      const result = await analyzeCode(formData);
      setAnalysisResult(result);
      showNotification('Анализ успешно завершен', 'success');
    } catch (error) {
      console.error('Ошибка при анализе кода:', error);
      showNotification(
        'Ошибка при анализе кода. ' + 
        (error.response ? error.response.data.detail || error.message : error.message),
        'error'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="app-background">
        <Header />
        <Container maxWidth="xl">
          <Fade in={apiStatus.checked && !apiStatus.isOnline} timeout={500}>
            <Box sx={{ mb: 3 }}>
              {apiStatus.checked && !apiStatus.isOnline && (
                <Alert 
                  severity="error" 
                  variant="filled"
                  sx={{ 
                    mb: 3, 
                    boxShadow: theme.shadows[3],
                    animation: 'glow 2s infinite'
                  }}
                >
                  API недоступен. Убедитесь, что сервер запущен на порту 8082.
                </Alert>
              )}
            </Box>
          </Fade>
          
          {apiStatus.checking ? (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center',
              alignItems: 'center',
              height: '200px',
              flexDirection: 'column'
            }}>
              <CircularProgress color="secondary" sx={{ mb: 2 }} />
              <Box sx={{ color: 'text.secondary' }}>Проверка соединения с API...</Box>
            </Box>
          ) : (
            <>
              <Grow in={true} timeout={800}>
                <div>
                  <ExamplesSelector onExampleSelect={handleExampleSelect} />
                </div>
              </Grow>
              
              <Grow in={true} timeout={1000}>
                <div>
                  <CodeForm 
                    onAnalyzeSubmit={handleAnalyzeSubmit} 
                    loading={loading}
                    disabled={!apiStatus.isOnline}
                    initialData={selectedExample}
                  />
                </div>
              </Grow>
              
              {loading && (
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'center',
                  my: 4,
                  flexDirection: 'column',
                  alignItems: 'center'
                }}>
                  <CircularProgress 
                    color="primary" 
                    size={60} 
                    thickness={4} 
                    sx={{ 
                      boxShadow: '0 0 20px rgba(252, 4, 116, 0.3)',
                      borderRadius: '50%',
                      p: 1
                    }} 
                  />
                  <Box sx={{ mt: 2, color: 'text.secondary', fontStyle: 'italic' }}>
                    Анализируем код с помощью ИИ...
                  </Box>
                </Box>
              )}
              
              {analysisResult && (
                <Grow in={true} timeout={1200}>
                  <div>
                    <AnalysisReport analysisResult={analysisResult} />
                  </div>
                </Grow>
              )}
            </>
          )}

          <Snackbar
            open={notification.open}
            autoHideDuration={6000}
            onClose={handleCloseNotification}
            TransitionComponent={Grow}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert 
              onClose={handleCloseNotification} 
              severity={notification.severity}
              variant="filled"
              elevation={6}
              sx={{ width: '100%' }}
            >
              {notification.message}
            </Alert>
          </Snackbar>
        </Container>
      </div>
    </ThemeProvider>
  );
};

export default App; 