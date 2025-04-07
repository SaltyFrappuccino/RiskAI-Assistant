import React, { useState } from 'react';
import { 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Box, 
  Paper,
  Typography,
  useTheme,
  Tooltip,
  IconButton,
  Collapse,
  Zoom,
  Chip
} from '@mui/material';
import { examples } from '../data/examples';

/**
 * Компонент для выбора примера из предустановленного списка
 * @param {Object} props - свойства компонента
 * @param {Function} props.onExampleSelect - функция, вызываемая при выборе примера
 */
const ExamplesSelector = ({ onExampleSelect }) => {
  const theme = useTheme();
  const [selectedIndex, setSelectedIndex] = useState('');
  const [showInfo, setShowInfo] = useState(false);
  
  const handleExampleChange = (event) => {
    const index = event.target.value;
    setSelectedIndex(index);
    
    const selectedExample = examples.find((ex, i) => i === index);
    if (selectedExample) {
      onExampleSelect(selectedExample);
    }
  };

  const toggleInfo = () => {
    setShowInfo(!showInfo);
  };

  const exampleDescriptions = {
    0: 'Хороший пример с полной валидацией входных данных, четкой документацией, хорошим покрытием тестами и следованием лучшим практикам разработки.',
    1: 'Средний пример с базовой валидацией входных данных, пропусками в документации и неполным покрытием тестами.',
    2: 'Плохой пример с минимальной валидацией, использованием print вместо исключений, отсутствием округления, небрежной организацией кода и ошибками в тестах.'
  };

  const qualityIcons = {
    0: '✅',
    1: '⚠️',
    2: '❌'
  };

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 3, 
        mb: 4, 
        borderRadius: 4,
        background: `linear-gradient(135deg, 
          ${theme.palette.background.paper} 0%, 
          ${theme.palette.background.paper} 95%, 
          ${theme.palette.primary.dark} 100%)`,
        boxShadow: '0 8px 20px rgba(0, 0, 0, 0.15)',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: '0 12px 28px rgba(0, 0, 0, 0.2)',
          transform: 'translateY(-2px)'
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '150px',
          height: '150px',
          background: 'radial-gradient(circle, rgba(109, 22, 165, 0.08) 0%, transparent 70%)',
          zIndex: 0,
          borderRadius: '0 0 0 100%'
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', mb: showInfo ? 3 : 0 }}>
        <Typography 
          variant="h6" 
          sx={{ 
            mr: 3, 
            color: theme.palette.primary.main,
            fontWeight: 'bold',
            position: 'relative',
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: -5,
              left: 0,
              height: '2px',
              width: '40%',
              backgroundImage: theme.palette.gradient.primary,
              borderRadius: '2px'
            }
          }}
        >
          Готовые примеры
        </Typography>
        
        <FormControl 
          sx={{ 
            minWidth: { xs: '100%', sm: 350 }, 
            mr: 2,
            mt: { xs: 2, sm: 0 },
            position: 'relative',
            zIndex: 1
          }}
        >
          <InputLabel id="example-select-label">Выберите пример для загрузки</InputLabel>
          <Select
            labelId="example-select-label"
            id="example-select"
            value={selectedIndex}
            label="Выберите пример для загрузки"
            onChange={handleExampleChange}
            MenuProps={{
              PaperProps: {
                sx: {
                  borderRadius: 3,
                  boxShadow: '0 8px 16px rgba(0, 0, 0, 0.15)',
                  backgroundImage: 'none',
                  background: theme.palette.background.paper,
                }
              }
            }}
          >
            <MenuItem value="" disabled>
              <em>Выберите пример</em>
            </MenuItem>
            
            {examples.map((example, index) => (
              <MenuItem 
                key={index} 
                value={index}
                sx={{
                  borderLeft: '3px solid transparent',
                  borderImageSlice: 1,
                  borderImageSource: index === 0 
                    ? 'linear-gradient(to bottom, #66BB6A, #43A047)'
                    : index === 1 
                    ? 'linear-gradient(to bottom, #FFA726, #FB8C00)'
                    : 'linear-gradient(to bottom, #FF4A4A, #D32F2F)',
                  transition: 'all 0.2s ease',
                  '&.Mui-selected': {
                    backgroundColor: index === 0 
                      ? 'rgba(102, 187, 106, 0.08)'
                      : index === 1 
                      ? 'rgba(255, 167, 38, 0.08)'
                      : 'rgba(255, 74, 74, 0.08)',
                  },
                  '&:hover': {
                    backgroundColor: index === 0 
                      ? 'rgba(102, 187, 106, 0.15)'
                      : index === 1 
                      ? 'rgba(255, 167, 38, 0.15)'
                      : 'rgba(255, 74, 74, 0.15)',
                    borderImageSource: index === 0 
                      ? 'linear-gradient(to bottom, #81C784, #66BB6A)'
                      : index === 1 
                      ? 'linear-gradient(to bottom, #FFB74D, #FFA726)'
                      : 'linear-gradient(to bottom, #FF7373, #FF4A4A)',
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Typography sx={{ mr: 1, fontSize: '1rem' }}>
                    {qualityIcons[index]}
                  </Typography>
                  {example.title}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Tooltip 
          title={showInfo ? "Скрыть информацию" : "Информация о примерах"} 
          arrow
          TransitionComponent={Zoom}
        >
          <IconButton 
            color="primary" 
            onClick={toggleInfo}
            size="small"
            sx={{ 
              bgcolor: showInfo ? 'rgba(252, 4, 116, 0.15)' : 'transparent',
              '&:hover': {
                bgcolor: 'rgba(252, 4, 116, 0.2)',
                transform: 'rotate(15deg)'
              },
              transition: 'all 0.3s ease',
              border: '2px solid',
              borderColor: 'primary.main',
              ml: { xs: 0, sm: 'auto' },
              mt: { xs: 2, sm: 0 },
              width: 36,
              height: 36
            }}
          >
            <Typography 
              variant="button" 
              sx={{ 
                fontWeight: 'bold',
                fontSize: '1rem'
              }}
            >
              i
            </Typography>
          </IconButton>
        </Tooltip>
      </Box>
      
      <Collapse in={showInfo} timeout={500}>
        <Box 
          sx={{ 
            p: 2.5,
            borderLeft: `4px solid ${theme.palette.secondary.main}`,
            bgcolor: 'rgba(109, 22, 165, 0.08)',
            borderRadius: '0 16px 16px 0',
            boxShadow: 'inset 0 0 20px rgba(0, 0, 0, 0.05)',
            position: 'relative',
            overflow: 'hidden',
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: 0,
              right: 0,
              width: '100px',
              height: '100px',
              background: 'radial-gradient(circle, rgba(252, 4, 116, 0.05) 0%, transparent 70%)',
              zIndex: 0
            }
          }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontStyle: 'italic' }}>
            Выберите один из примеров для тестирования анализатора кода:
          </Typography>
          
          {Object.entries(exampleDescriptions).map(([index, description]) => (
            <Box 
              key={index} 
              sx={{ 
                mb: 1.5,
                display: 'flex',
                alignItems: 'flex-start',
                position: 'relative',
                zIndex: 1
              }}
            >
              <Chip 
                label={examples[index].title} 
                size="small"
                color={index === '0' ? 'success' : index === '1' ? 'warning' : 'error'}
                sx={{ 
                  mr: 1.5,
                  minWidth: '150px',
                  fontWeight: 500,
                  boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
                }}
              />
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'text.primary',
                  pt: '3px'
                }}
              >
                {description}
              </Typography>
            </Box>
          ))}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default ExamplesSelector; 