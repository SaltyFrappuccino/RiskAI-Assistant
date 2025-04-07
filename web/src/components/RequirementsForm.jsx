import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography, 
  CircularProgress,
  FormControlLabel,
  Switch,
  Divider,
  Grid,
  Tooltip,
} from '@mui/material';

/**
 * Компонент формы для анализа требований
 * 
 * @param {Object} props - Свойства компонента
 * @param {Function} props.onRequirementsSubmit - Функция, вызываемая при отправке формы
 * @param {boolean} props.loading - Флаг загрузки
 * @param {boolean} props.disabled - Флаг деактивации формы
 */
const RequirementsForm = ({ onRequirementsSubmit, loading, disabled }) => {
  const [formData, setFormData] = useState({
    requirements: '',
    guidelines: '',
    use_cache: true
  });

  const [showGuidelines, setShowGuidelines] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setFormData({
      ...formData,
      [name]: checked
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onRequirementsSubmit(formData);
  };

  const handleClear = () => {
    setFormData({
      requirements: '',
      guidelines: '',
      use_cache: true
    });
  };

  const toggleGuidelines = () => {
    setShowGuidelines(!showGuidelines);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Анализ требований
        </Typography>
        <Box>
          <Tooltip title="Инструкция">
            <span style={{ cursor: 'help', fontSize: '24px' }}>❓</span>
          </Tooltip>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label="Требования"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              multiline
              rows={10}
              fullWidth
              variant="outlined"
              required
              disabled={disabled || loading}
              placeholder="Введите требования для анализа"
              helperText="Введите требования к проекту или продукту, которые нужно проанализировать"
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Button
                variant="text"
                color="primary"
                onClick={toggleGuidelines}
                sx={{ textTransform: 'none' }}
              >
                <span style={{ marginRight: '8px', fontSize: '16px' }}>ℹ️</span>
                {showGuidelines ? 'Скрыть руководства' : 'Показать руководства'}
              </Button>
              <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                (опционально)
              </Typography>
            </Box>

            {showGuidelines && (
              <TextField
                label="Руководства"
                name="guidelines"
                value={formData.guidelines}
                onChange={handleChange}
                multiline
                rows={5}
                fullWidth
                variant="outlined"
                disabled={disabled || loading}
                placeholder="Введите руководства или стандарты для анализа требований"
                helperText="Вы можете указать свои собственные руководства или стандарты для анализа требований"
              />
            )}
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.use_cache}
                  onChange={handleSwitchChange}
                  name="use_cache"
                  color="primary"
                  disabled={disabled || loading}
                />
              }
              label="Использовать кэш"
            />
            <Tooltip title="Использование кэша позволяет ускорить анализ, если похожие требования уже анализировались ранее">
              <span style={{ cursor: 'help', fontSize: '16px', marginLeft: '4px' }}>❓</span>
            </Tooltip>
          </Grid>

          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleClear}
              disabled={disabled || loading}
            >
              Очистить
            </Button>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={!formData.requirements || disabled || loading}
              startIcon={loading && <CircularProgress size={20} color="inherit" />}
            >
              {loading ? 'Анализ...' : 'Анализировать требования'}
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default RequirementsForm; 