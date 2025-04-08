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
  styled,
  IconButton,
  Badge
} from '@mui/material';
import { keyframes } from '@emotion/react';
import { clearCache } from '../api/api';
import ExamplesSelector from './ExamplesSelector';

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

const pulse = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
`;

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

const CacheSwitchContainer = styled(Box)(({ theme }) => ({
  padding: '8px 15px',
  borderRadius: '15px',
  marginLeft: theme.spacing(2),
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(25, 118, 210, 0.05)',
    borderRadius: 'inherit',
    zIndex: -1,
  }
}));

const AnimatedCacheIcon = styled('span')(({ theme, active }) => ({
  animation: active ? `${pulse} 2s infinite ease-in-out` : 'none',
  color: active ? theme.palette.primary.main : theme.palette.text.secondary,
  marginLeft: theme.spacing(1),
  fontFamily: 'monospace',
  fontSize: '18px',
  verticalAlign: 'middle',
  position: 'relative',
  top: -1
}));

const GradientText = styled(Typography)(({ theme, color = 'primary' }) => {
  const gradients = {
    primary: 'linear-gradient(45deg, #6D16A5 30%, #FC0474 90%)',
    extreme: 'linear-gradient(45deg, #FF007A 30%, #9C27B0 90%)',
    cache: 'linear-gradient(45deg, #1976D2 30%, #64B5F6 90%)'
  };
  return {
    background: gradients[color] || gradients.primary,
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
 * @param {Object} props.cacheStats - статистика использования кэша (опционально)
 */
const CodeForm = ({ onAnalyzeSubmit, loading, disabled, initialData, cacheStats }) => {
  const [formData, setFormData] = useState({
    story: '',
    requirements: '',
    code: '',
    test_cases: '',
    enable_preprocessing: true,
    extreme_mode: false,
    use_cache: true
  });
  
  const [clearingCache, setClearingCache] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        story: initialData.story || '',
        requirements: initialData.requirements || '',
        code: initialData.code || '',
        test_cases: initialData.test_cases || '',
        enable_preprocessing: true,
        extreme_mode: false,
        use_cache: true
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    
    if (name === 'enable_preprocessing' && !checked) {
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

  const handleSubmit = (e) => {
    e.preventDefault();
    onAnalyzeSubmit(formData);
  };

  const handleClear = () => {
    setFormData({
      story: '',
      requirements: '',
      code: '',
      test_cases: '',
      enable_preprocessing: true,
      extreme_mode: false,
      use_cache: true
    });
  };
  
  const handleClearCache = async () => {
    try {
      setClearingCache(true);
      await clearCache();
      setClearingCache(false);
    } catch (error) {
      console.error('Ошибка при очистке кэша:', error);
      setClearingCache(false);
    }
  };
  
  const cacheHitCount = cacheStats?.cache_hits || 0;

  return (
    <Paper elevation={3}>
      <Box p={3}>
        <Typography variant="h5" gutterBottom align="center" color="primary">
          Анализ артефактов с использованием ИИ
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
            
            <Grid item xs={12}>
              <Box 
                display="flex" 
                flexDirection={{ xs: 'column', sm: 'row' }} 
                alignItems="center" 
                justifyContent="center"
                gap={2}
                flexWrap="wrap"
              >
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
                
                {/* Переключатель использования кэша */}
                <CacheSwitchContainer>
                  <Tooltip title="Включить использование кэша для ускорения анализа. При повторном анализе похожего кода будут использоваться сохраненные результаты">
                    <FormControlLabel
                      control={
                        <Switch
                          name="use_cache"
                          checked={formData.use_cache}
                          onChange={handleSwitchChange}
                          color="primary"
                        />
                      }
                      label={
                        <Box display="flex" alignItems="center">
                          <GradientText color="cache">
                            Использовать кэш
                          </GradientText>
                          <Badge badgeContent={cacheHitCount} color="primary" max={999} showZero={false}>
                            <AnimatedCacheIcon active={formData.use_cache && cacheHitCount > 0}>
                              💾
                            </AnimatedCacheIcon>
                          </Badge>
                        </Box>
                      }
                    />
                  </Tooltip>
                  
                  {/* Кнопка очистки кэша */}
                  <Tooltip title="Очистить кэш">
                    <span style={{ display: 'inline-block', marginLeft: '8px' }}>
                      <IconButton 
                        size="small" 
                        onClick={handleClearCache} 
                        disabled={clearingCache || !formData.use_cache}
                        color="primary"
                      >
                        {clearingCache ? (
                          <CircularProgress size={20} />
                        ) : (
                          <span style={{ fontSize: '16px' }}>🗑️</span>
                        )}
                      </IconButton>
                    </span>
                  </Tooltip>
                </CacheSwitchContainer>
              </Box>
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