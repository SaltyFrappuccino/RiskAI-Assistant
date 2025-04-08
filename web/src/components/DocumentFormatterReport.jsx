import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  useTheme,
  IconButton,
  Tooltip,
  Alert,
  TextField,
  Button,
  CircularProgress,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText
} from '@mui/material';

/**
 * Компонент для отображения результатов форматирования документа
 * @param {Object} props - свойства компонента
 * @param {Object} props.formatterResult - результат форматирования
 * @param {Function} props.onContinueFormatting - функция для продолжения диалога с форматировщиком
 * @param {boolean} props.loading - индикатор загрузки
 */
const DocumentFormatterReport = ({ formatterResult, onContinueFormatting, loading }) => {
  const theme = useTheme();
  const [copySuccess, setCopySuccess] = useState(false);
  const [userMessage, setUserMessage] = useState('');
  
  if (!formatterResult || !formatterResult.formatted_content) {
    return null;
  }
  
  /**
   * Обработчик копирования текста в буфер обмена
   */
  const handleCopy = () => {
    navigator.clipboard.writeText(formatterResult.formatted_content);
    setCopySuccess(true);
    
    // Сбрасываем статус копирования через 2 секунды
    setTimeout(() => {
      setCopySuccess(false);
    }, 2000);
  };
  
  /**
   * Обработчик отправки сообщения пользователя
   * @param {Event} e - событие формы
   */
  const handleMessageSend = (e) => {
    e.preventDefault();
    if (!userMessage.trim()) return;
    
    onContinueFormatting(userMessage);
    setUserMessage('');
  };
  
  // Проверяем, завершено ли форматирование
  const isFormatCompleted = formatterResult.is_completed;
  
  // Получаем историю диалога
  const conversationHistory = formatterResult.conversation_history || [];
  
  // Фильтруем историю, чтобы показывать только сообщения после первого запроса
  const chatHistory = conversationHistory.length > 2 
    ? conversationHistory.slice(1) 
    : [];
  
  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" component="h2">
          Отформатированный документ
        </Typography>
        
        <Box>
          <Tooltip title="Копировать текст">
            <IconButton onClick={handleCopy} color={copySuccess ? "success" : "default"}>
              {copySuccess ? <span style={{ fontSize: '1.2em' }}>✅</span> : <span style={{ fontSize: '1.2em' }}>📋</span>}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {!isFormatCompleted && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Документ в процессе форматирования. Ответьте на вопросы, чтобы получить окончательный результат.
        </Alert>
      )}
      
      {isFormatCompleted && formatterResult.comments && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {formatterResult.comments}
        </Alert>
      )}
      
      <Box 
        sx={{ 
          p: 2, 
          bgcolor: theme.palette.background.paper, 
          borderRadius: 1,
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          overflow: 'auto',
          maxHeight: '400px',
          mb: 3
        }}
      >
        {formatterResult.formatted_content}
      </Box>
      
      {/* История диалога */}
      {chatHistory.length > 0 && (
        <>
          <Typography variant="h6" component="h3" sx={{ mt: 4, mb: 2 }}>
            История диалога
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <List sx={{ width: '100%', bgcolor: 'background.paper', mb: 3, p: 2, borderRadius: 1 }}>
            {chatHistory.map((message, index) => (
              <ListItem key={index} alignItems="flex-start" sx={{ 
                mb: 1,
                bgcolor: message.role === 'assistant' ? 'rgba(25, 118, 210, 0.05)' : 'rgba(76, 175, 80, 0.05)',
                borderRadius: 1,
                p: 2
              }}>
                <ListItemAvatar>
                  <Avatar sx={{ 
                    bgcolor: message.role === 'assistant' ? theme.palette.primary.main : theme.palette.success.main
                  }}>
                    {message.role === 'assistant' ? '🤖' : '👤'}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={message.role === 'assistant' ? 'Ассистент' : 'Вы'}
                  secondary={
                    <Typography
                      sx={{ display: 'inline', whiteSpace: 'pre-wrap' }}
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      {message.content}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </>
      )}
      
      {/* Форма для ввода сообщения пользователя */}
      {!isFormatCompleted && (
        <Box component="form" onSubmit={handleMessageSend} sx={{ mt: 3 }}>
          <Typography variant="h6" component="h3" sx={{ mb: 2 }}>
            Ответить ассистенту
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={2}
              placeholder="Введите ваш ответ..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              disabled={loading}
              InputProps={{
                sx: { fontFamily: 'inherit' }
              }}
            />
            <Button
              variant="contained"
              color="primary"
              endIcon={loading ? <CircularProgress size={20} /> : <span>➤</span>}
              type="submit"
              disabled={loading || !userMessage.trim()}
              sx={{ alignSelf: 'flex-end', minWidth: 100 }}
            >
              {loading ? 'Отправка...' : 'Отправить'}
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default DocumentFormatterReport;