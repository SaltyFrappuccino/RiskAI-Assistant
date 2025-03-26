import React, { useState, useEffect } from 'react';
import { 
  TextField, 
  Button, 
  Box, 
  Paper, 
  Typography, 
  Grid,
  CircularProgress,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material';

/**
 * Компонент формы для ввода данных для анализа кода
 * @param {Object} props - свойства компонента
 * @param {Function} props.onAnalyzeSubmit - функция, вызываемая при отправке формы
 * @param {boolean} props.loading - флаг загрузки
 * @param {boolean} props.disabled - флаг отключения формы
 * @param {Object} props.initialData - начальные данные для формы (опционально)
 */
const CodeForm = ({ onAnalyzeSubmit, loading, disabled, initialData }) => {
  // Состояние формы
  const [formData, setFormData] = useState({
    story: '',
    requirements: '',
    code: '',
    test_cases: '',
    extreme_mode: false
  });

  // Обновляем данные формы при изменении initialData
  useEffect(() => {
    if (initialData) {
      setFormData({
        story: initialData.story || '',
        requirements: initialData.requirements || '',
        code: initialData.code || '',
        test_cases: initialData.test_cases || '',
        extreme_mode: false
      });
    }
  }, [initialData]);

  // Обработчик изменения полей формы
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  // Обработчик изменения переключателя
  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: checked
    }));
  };

  // Обработчик отправки формы
  const handleSubmit = (e) => {
    e.preventDefault();
    onAnalyzeSubmit(formData);
  };

  // Обработчик очистки формы
  const handleClear = () => {
    setFormData({
      story: '',
      requirements: '',
      code: '',
      test_cases: '',
      extreme_mode: false
    });
  };

  return (
    <Paper elevation={3}>
      <Box p={3}>
        <Typography variant="h5" gutterBottom align="center" color="primary">
          Анализ кода с использованием ИИ
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Story"
                name="story"
                value={formData.story}
                onChange={handleChange}
                placeholder="Введите краткое описание задачи"
                multiline
                rows={4}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Требования"
                name="requirements"
                value={formData.requirements}
                onChange={handleChange}
                placeholder="Введите требования к продукту"
                multiline
                rows={4}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Код"
                name="code"
                value={formData.code}
                onChange={handleChange}
                placeholder="Введите код, реализующий задачу"
                multiline
                rows={8}
                variant="outlined"
                InputProps={{
                  style: { fontFamily: 'monospace' }
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Тест-кейсы"
                name="test_cases"
                value={formData.test_cases}
                onChange={handleChange}
                placeholder="Введите тест-кейсы для проверки кода"
                multiline
                rows={8}
                variant="outlined"
                InputProps={{
                  style: { fontFamily: 'monospace' }
                }}
              />
            </Grid>
            
            <Grid item xs={12} display="flex" flexDirection="column" alignItems="center">
              <Tooltip title="В экстремальном режиме предобработчик попытается максимально уменьшить размер текста для более эффективного анализа, сохраняя при этом смысл">
                <FormControlLabel
                  control={
                    <Switch
                      name="extreme_mode"
                      checked={formData.extreme_mode}
                      onChange={handleSwitchChange}
                      color="secondary"
                    />
                  }
                  label={
                    <Typography sx={{ display: 'flex', alignItems: 'center' }}>
                      <span style={{ 
                        background: '-webkit-linear-gradient(45deg, #FF007A 30%, #9C27B0 90%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontWeight: 'bold'
                      }}>
                        Экстремальный режим предобработки
                      </span>
                    </Typography>
                  }
                />
              </Tooltip>
            </Grid>
            
            <Grid item xs={12} display="flex" justifyContent="center" gap={2}>
              <Button 
                type="submit"
                variant="contained" 
                color="primary" 
                size="large"
                disabled={loading || disabled}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {loading ? 'Анализ...' : 'Анализировать код'}
              </Button>
              
              <Button 
                variant="outlined" 
                color="secondary" 
                size="large"
                onClick={handleClear}
                disabled={loading || disabled}
              >
                Очистить
              </Button>
            </Grid>
          </Grid>
        </form>
      </Box>
    </Paper>
  );
};

export default CodeForm; 