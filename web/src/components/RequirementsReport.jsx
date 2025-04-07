import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Tabs, 
  Tab, 
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Grid,
  Chip,
  LinearProgress,
  Card, 
  CardContent,
  Tooltip
} from '@mui/material';

/**
 * Компонент для отображения результатов анализа требований
 * 
 * @param {Object} props - Свойства компонента
 * @param {Object} props.requirementsResult - Результат анализа требований
 */
const RequirementsReport = ({ requirementsResult }) => {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  const getIcon = (severity) => {
    if (severity === 'низкая' || severity === 'low') return <span style={{ fontSize: '20px' }}>⚠️</span>;
    if (severity === 'средняя' || severity === 'medium') return <span style={{ fontSize: '20px' }}>⚠️</span>;
    if (severity === 'высокая' || severity === 'high') return <span style={{ fontSize: '20px', color: 'red' }}>❗</span>;
    if (severity === 'критическая' || severity === 'critical') return <span style={{ fontSize: '20px', color: 'red' }}>🛑</span>;
    return <span style={{ fontSize: '20px' }}>❓</span>;
  };

  const renderScoreCard = (title, score, description) => (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h4" color={getScoreColor(score)} sx={{ mr: 2 }}>
            {score}
          </Typography>
          <Tooltip title={description || ''}>
            <span style={{ cursor: 'help', fontSize: '16px' }}>❓</span>
          </Tooltip>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={score} 
          color={score >= 80 ? 'success' : score >= 60 ? 'warning' : 'error'} 
          sx={{ height: 8, borderRadius: 5 }}
        />
      </CardContent>
    </Card>
  );

  const renderAssessment = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Общая оценка
      </Typography>
      <Paper variant="outlined" sx={{ p: 2, my: 2, bgcolor: 'background.paper' }}>
        <Typography variant="body1">
          {requirementsResult.overall_assessment}
        </Typography>
      </Paper>

      <Grid container spacing={2} sx={{ my: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          {renderScoreCard('Общий балл', requirementsResult.total_score, 'Общая оценка качества требований')}
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          {renderScoreCard('Ясность', requirementsResult.clarity_score, 'Оценка ясности и конкретности требований')}
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          {renderScoreCard('Полнота', requirementsResult.completeness_score, 'Оценка полноты требований')}
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          {renderScoreCard('Непротиворечивость', requirementsResult.consistency_score, 'Оценка непротиворечивости требований')}
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          {renderScoreCard('Проверяемость', requirementsResult.testability_score, 'Оценка проверяемости требований')}
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          {renderScoreCard('Реализуемость', requirementsResult.feasibility_score, 'Оценка реализуемости требований')}
        </Grid>
      </Grid>
    </Box>
  );

  const renderProblematicRequirements = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Проблемные требования
      </Typography>
      
      {requirementsResult.problematic_requirements.length === 0 ? (
        <Typography variant="body1" sx={{ my: 2, color: 'success.main' }}>
          Проблемных требований не обнаружено! 🎉
        </Typography>
      ) : (
        <List>
          {requirementsResult.problematic_requirements.map((req, index) => (
            <Paper key={index} variant="outlined" sx={{ mb: 2, overflow: 'hidden' }}>
              <ListItem 
                alignItems="flex-start"
                sx={{ 
                  borderLeft: 4, 
                  borderColor: 
                    req.severity === 'critical' ? 'error.main' : 
                    req.severity === 'high' ? 'error.light' :
                    req.severity === 'medium' ? 'warning.main' : 'info.main'
                }}
              >
                <ListItemIcon>
                  {getIcon(req.severity)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {req.requirement}
                      </Typography>
                      <Chip 
                        label={req.category || req.type || 'Проблема'} 
                        size="small" 
                        color={
                          req.severity === 'critical' || req.severity === 'high' ? 'error' : 
                          req.severity === 'medium' ? 'warning' : 'info'
                        }
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {req.description || req.problem}
                      </Typography>
                      {req.recommendation && (
                        <Box sx={{ mt: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                          <Typography variant="body2" color="primary">
                            <strong>Рекомендация:</strong> {req.recommendation}
                          </Typography>
                        </Box>
                      )}
                    </>
                  }
                />
              </ListItem>
            </Paper>
          ))}
        </List>
      )}
    </Box>
  );

  const renderMissingAspects = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Недостающие аспекты
      </Typography>
      
      {requirementsResult.missing_aspects.length === 0 ? (
        <Typography variant="body1" sx={{ my: 2, color: 'success.main' }}>
          Недостающих аспектов не обнаружено! 🎉
        </Typography>
      ) : (
        <List>
          {requirementsResult.missing_aspects.map((aspect, index) => (
            <ListItem key={index} divider>
              <ListItemIcon>
                <span style={{ fontSize: '20px' }}>❓</span>
              </ListItemIcon>
              <ListItemText primary={aspect} />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );

  const renderImprovementSuggestions = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Предложения по улучшению
      </Typography>
      
      {requirementsResult.improvement_suggestions.length === 0 ? (
        <Typography variant="body1" sx={{ my: 2, color: 'info.main' }}>
          Предложений по улучшению нет.
        </Typography>
      ) : (
        <List>
          {requirementsResult.improvement_suggestions.map((suggestion, index) => (
            <ListItem key={index} divider>
              <ListItemIcon>
                <span style={{ fontSize: '20px' }}>💡</span>
              </ListItemIcon>
              <ListItemText primary={suggestion} />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );

  const getTabContent = () => {
    switch (currentTab) {
      case 0:
        return renderAssessment();
      case 1:
        return renderProblematicRequirements();
      case 2:
        return renderMissingAspects();
      case 3:
        return renderImprovementSuggestions();
      default:
        return renderAssessment();
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <span style={{ fontSize: '24px', marginRight: '8px' }}>📊</span>
        <Typography variant="h5" component="h2">
          Результаты анализа требований
        </Typography>
      </Box>
      
      <Divider sx={{ mb: 3 }} />
      
      <Tabs value={currentTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Общая оценка" />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              Проблемные требования
              {requirementsResult.problematic_requirements.length > 0 && (
                <Chip 
                  label={requirementsResult.problematic_requirements.length} 
                  size="small" 
                  color="error" 
                  sx={{ ml: 1, height: 20, minWidth: 20 }} 
                />
              )}
            </Box>
          } 
        />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              Недостающие аспекты
              {requirementsResult.missing_aspects.length > 0 && (
                <Chip 
                  label={requirementsResult.missing_aspects.length} 
                  size="small" 
                  color="warning" 
                  sx={{ ml: 1, height: 20, minWidth: 20 }} 
                />
              )}
            </Box>
          } 
        />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              Предложения
              {requirementsResult.improvement_suggestions.length > 0 && (
                <Chip 
                  label={requirementsResult.improvement_suggestions.length} 
                  size="small" 
                  color="info" 
                  sx={{ ml: 1, height: 20, minWidth: 20 }} 
                />
              )}
            </Box>
          } 
        />
      </Tabs>
      
      {getTabContent()}
    </Paper>
  );
};

export default RequirementsReport; 