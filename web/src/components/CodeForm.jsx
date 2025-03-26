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
  Tooltip,
  Slide,
  Fade,
  styled
} from '@mui/material';
import { keyframes } from '@emotion/react';

// Определение анимации свечения
const glow = keyframes`
  0% {
    box-shadow: 0 0 5px rgba(252, 4, 116, 0.4);
  }
  50% {
    box-shadow: 0 0 15px rgba(252, 4, 116, 0.7), 0 0 25px rgba(109, 22, 165, 0.5);
  }
  100% {
    box-shadow: 0 0 5px rgba(252, 4, 116, 0.4);
  }
`;

// Стилизованный контейнер для переключателя экстремального режима
const ExtremeModeSwitchContainer = styled(Box)(({ theme }) => ({
  padding: '8px 15px',
  borderRadius: '15px',
  marginLeft: theme.spacing(2),
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  animation: `${glow} 3s infinite ease-in-out`,
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(252, 4, 116, 0.05)',
    borderRadius: 'inherit',
    zIndex: -1,
  }
}));

// Градиентный текст для переключателей
const GradientText = styled(Typography)(({ theme, color = 'primary' }) => {
  const gradients = {
    primary: 'linear-gradient(45deg, #6D16A5 30%, #FC0474 90%)',
    extreme: 'linear-gradient(45deg, #FF007A 30%, #9C27B0 90%)'
  };
  return {
    background: gradients[color],
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
  };
});

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
    enable_preprocessing: true,
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
        enable_preprocessing: true,
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
    
    if (name === 'enable_preprocessing' && !checked) {
      // Если отключаем предобработку, также отключаем и экстремальный режим
      setFormData(prevData => ({
        ...prevData,
        [name]: checked,
        extreme_mode: false
      }));
    } else {
      setFormData(prevData => ({
        ...prevData,
        [name]: checked
      }));
    }
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
      enable_preprocessing: true,
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
            
            <Grid item xs={12} display="flex" flexDirection="row" alignItems="center" justifyContent="center">
              {/* Переключатель предобработки */}
              <Tooltip title="Включить предобработку данных для улучшения форматирования и структуры текста">
                <FormControlLabel
                  control={
                    <Switch
                      name="enable_preprocessing"
                      checked={formData.enable_preprocessing}
                      onChange={handleSwitchChange}
                      color="primary"
                    />
                  }
                  label={
                    <GradientText color="primary">
                      Предобработка текста
                    </GradientText>
                  }
                />
              </Tooltip>
              
              {/* Переключатель экстремального режима с анимацией */}
              <Slide 
                direction="left" 
                in={formData.enable_preprocessing} 
                mountOnEnter 
                unmountOnExit
                timeout={{ enter: 500, exit: 300 }}
              >
                <Fade in={formData.enable_preprocessing} timeout={{ enter: 800, exit: 300 }}>
                  <ExtremeModeSwitchContainer>
                    <Tooltip title="В экстремальном режиме предобработчик попытается максимально уменьшить размер текста для более эффективного анализа, сохраняя при этом смысл">
                      <FormControlLabel
                        control={
                          <Switch
                            name="extreme_mode"
                            checked={formData.extreme_mode}
                            onChange={handleSwitchChange}
                            color="secondary"
                            disabled={!formData.enable_preprocessing}
                          />
                        }
                        label={
                          <GradientText color="extreme">
                            Экстремальный режим
                          </GradientText>
                        }
                      />
                    </Tooltip>
                  </ExtremeModeSwitchContainer>
                </Fade>
              </Slide>
            </Grid>
            
            <Grid item xs={12} display="flex" justifyContent="center" gap={2} mt={2}>
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