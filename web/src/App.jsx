import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Paper, CircularProgress, Snackbar, Alert, Tabs, Tab } from '@mui/material';
import theme from './styles/theme';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import Grow from '@mui/material/Grow';
import ExamplesSelector from './components/ExamplesSelector';
import AnalysisReport from './components/AnalysisReport';
import RequirementsForm from './components/RequirementsForm';
import RequirementsReport from './components/RequirementsReport';
import DocumentFormatterForm from './components/DocumentFormatterForm';
import DocumentFormatterReport from './components/DocumentFormatterReport';
import Header from './components/Header';
import { analyzeCode, checkApiHealth, getCacheStats, analyzeRequirements, formatDocument, continueFormatting } from './api/api';
import './styles/globalStyles.css';
import CodeForm from './components/CodeForm';

/**
 * Главный компонент приложения с современным дизайном и анимациями
 */
const App = () => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [requirementsResult, setRequirementsResult] = useState(null);
  const [formatterResult, setFormatterResult] = useState(null);
  
  const [loading, setLoading] = useState(false);
  
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  
  const [apiStatus, setApiStatus] = useState('checking');

  const [selectedExample, setSelectedExample] = useState(null);
  
  const [cacheStats, setCacheStats] = useState(null);

  const [currentTab, setCurrentTab] = useState(0);
  
  const [formatterData, setFormatterData] = useState({
    template_rules: '',
    document_content: '',
    use_cache: true
  });

  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await checkApiHealth();
        setApiStatus(response.status === 'ok' ? 'online' : 'error');
        
        if (response.status === 'ok') {
          fetchCacheStats();
        }
      } catch (error) {
        setApiStatus('error');
        showNotification('API недоступен. Убедитесь, что сервер запущен на порту 8082.', 'error');
      }
    };

    checkApiStatus();
  }, []);
  
  const fetchCacheStats = async () => {
    try {
      const stats = await getCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.error('Ошибка при получении статистики кэша:', error);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({
      open: true,
      message,
      severity
    });
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({
      ...prev,
      open: false
    }));
  };

  const handleExampleSelect = (example) => {
    setSelectedExample(example);
    showNotification(`Пример "${example.title}" загружен`, 'success');
  };

  const handleAnalyzeSubmit = async (formData) => {
    if (!formData.code.trim()) {
      showNotification('Необходимо заполнить поле "Код" для анализа', 'warning');
      return;
    }

    setLoading(true);
    setAnalysisResult(null);

    try {
      const result = await analyzeCode(formData);
      setAnalysisResult(result);
      
      const cacheHits = result.cache_stats?.cache_hits || 0;
      const cacheMessage = cacheHits > 0 
        ? `Анализ завершен. Найдено ${cacheHits} элемент(ов) в кэше.` 
        : 'Анализ успешно завершен';
      
      showNotification(cacheMessage, 'success');
      
      fetchCacheStats();
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

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleRequirementsSubmit = async (formData) => {
    setLoading(true);
    try {
      const result = await analyzeRequirements(formData);
      setRequirementsResult(result);
      showNotification('Анализ требований успешно выполнен', 'success');
    } catch (error) {
      showNotification(`Ошибка при анализе требований: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFormatterSubmit = async (formData) => {
    if (!formData.template_rules.trim() || !formData.document_content.trim()) {
      showNotification('Необходимо заполнить поля "Шаблон/Правила" и "Документ" для форматирования', 'warning');
      return;
    }

    setLoading(true);
    setFormatterResult(null);
    setFormatterData(formData);

    try {
      const result = await formatDocument(formData);
      setFormatterResult(result);
      
      const isCompleted = result.is_completed;
      const message = isCompleted 
        ? 'Форматирование документа успешно завершено' 
        : 'Для завершения форматирования ответьте на вопросы ассистента';
      
      showNotification(message, 'success');
    } catch (error) {
      console.error('Ошибка при форматировании документа:', error);
      showNotification(
        'Ошибка при форматировании документа. ' + 
        (error.response ? error.response.data.detail || error.message : error.message),
        'error'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleContinueFormatting = async (userMessage) => {
    if (!userMessage.trim() || !formatterResult) {
      return;
    }

    setLoading(true);

    try {
      // Преобразуем объекты FormatterMessage в простые объекты для правильной сериализации
      const serializedHistory = formatterResult.conversation_history.map(msg => ({
        role: msg.role,
        content: msg.content,
        // Убедимся, что timestamp всегда строка в формате ISO
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : new Date(msg.timestamp).toISOString()
      }));
      
      const data = {
        user_message: userMessage,
        template_rules: formatterData.template_rules,
        document_content: formatterData.document_content,
        conversation_history: serializedHistory,
        use_cache: formatterData.use_cache
      };
      
      console.log('Sending data to continue formatting:', JSON.stringify(data)); // Отладочный лог
      
      const result = await continueFormatting(data);
      setFormatterResult(result);
      
      const isCompleted = result.is_completed;
      if (isCompleted) {
        showNotification('Форматирование документа успешно завершено', 'success');
      }
    } catch (error) {
      console.error('Ошибка при продолжении форматирования:', error);
      showNotification(
        'Ошибка при продолжении форматирования. ' + 
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
          <Paper sx={{ p: 2, mb: 2 }}>
            <Tabs value={currentTab} onChange={handleTabChange} centered>
              <Tab label="Анализ артефактов" />
              <Tab label="Анализ требований" />
              <Tab label="Форматирование документов" />
            </Tabs>
          </Paper>
          
          {apiStatus === 'checking' && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          )}
          
          {apiStatus === 'error' && (
            <Alert severity="error" sx={{ my: 2 }}>
              Не удалось подключиться к API. Пожалуйста, убедитесь, что сервер запущен.
            </Alert>
          )}
          
          {apiStatus === 'online' && (
            <Box>
              {currentTab === 0 && (
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
                        disabled={apiStatus !== 'online'}
                        initialData={selectedExample}
                        cacheStats={cacheStats}
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
              
              {currentTab === 1 && (
                <>
                  <RequirementsForm 
                    onRequirementsSubmit={handleRequirementsSubmit} 
                    loading={loading} 
                    disabled={apiStatus !== 'online'} 
                  />
                  {requirementsResult && <RequirementsReport requirementsResult={requirementsResult} />}
                </>
              )}
              
              {currentTab === 2 && (
                <>
                  <Grow in={true} timeout={800}>
                    <div>
                      <DocumentFormatterForm
                        onFormatterSubmit={handleFormatterSubmit}
                        loading={loading}
                        disabled={apiStatus !== 'online'}
                      />
                    </div>
                  </Grow>
                  
                  {loading && currentTab === 2 && (
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
                        {formatterResult ? 'Обрабатываем ваш ответ...' : 'Форматируем документ...'}
                      </Box>
                    </Box>
                  )}
                  
                  {formatterResult && (
                    <Grow in={true} timeout={1000}>
                      <div>
                        <DocumentFormatterReport 
                          formatterResult={formatterResult} 
                          onContinueFormatting={handleContinueFormatting} 
                          loading={loading}
                        />
                      </div>
                    </Grow>
                  )}
                </>
              )}
            </Box>
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