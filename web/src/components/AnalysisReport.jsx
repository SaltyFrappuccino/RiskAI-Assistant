import React from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  Divider, 
  LinearProgress, 
  Chip,
  Grid,
  Alert,
  Tabs,
  Tab,
  useTheme
} from '@mui/material';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

/**
 * Компонент для отображения результатов анализа кода
 * @param {Object} props - свойства компонента
 * @param {Object} props.analysisResult - результаты анализа
 */
const AnalysisReport = ({ analysisResult }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = React.useState(0);

  if (!analysisResult) {
    return null;
  }

  const { metrics, bugs, vulnerabilities, recommendations, summary } = analysisResult;

  // Обработчик изменения вкладки
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Генерация Markdown для метрик
  const generateMetricsMarkdown = () => {
    return `
## Метрики анализа

- **Соответствие кода требованиям**: ${metrics.code_requirements_match}%
- **Соответствие тест-кейсов требованиям**: ${metrics.test_requirements_match}%
- **Соответствие тест-кейсов коду**: ${metrics.test_code_match}%
    `;
  };

  // Генерация Markdown для багов
  const generateBugsMarkdown = () => {
    if (!bugs || bugs.length === 0) {
      return '## Баги\n\nБагов не обнаружено.';
    }

    let markdown = '## Найденные баги\n\n';
    
    bugs.forEach((bug, index) => {
      markdown += `### Баг ${index + 1}: ${bug.severity} приоритет\n\n`;
      markdown += `${bug.description}\n\n`;
      markdown += '```code\n' + bug.code_snippet + '\n```\n\n';
    });
    
    return markdown;
  };

  // Генерация Markdown для уязвимостей
  const generateVulnerabilitiesMarkdown = () => {
    if (!vulnerabilities || vulnerabilities.length === 0) {
      return '## Уязвимости\n\nУязвимостей не обнаружено.';
    }

    let markdown = '## Обнаруженные уязвимости\n\n';
    
    vulnerabilities.forEach((vuln, index) => {
      markdown += `### Уязвимость ${index + 1}: ${vuln.severity} риск\n\n`;
      markdown += `${vuln.description}\n\n`;
      markdown += '```code\n' + vuln.code_snippet + '\n```\n\n';
      markdown += `**Рекомендация по устранению**: ${vuln.mitigation}\n\n`;
    });
    
    return markdown;
  };

  // Генерация Markdown для рекомендаций
  const generateRecommendationsMarkdown = () => {
    if (!recommendations || recommendations.length === 0) {
      return '## Рекомендации\n\nРекомендаций нет.';
    }

    let markdown = '## Рекомендации по улучшению кода\n\n';
    
    recommendations.forEach((rec, index) => {
      markdown += `### Рекомендация ${index + 1}\n\n`;
      markdown += `${rec.description}\n\n`;
      markdown += '**Текущий код:**\n\n';
      markdown += '```code\n' + rec.code_snippet + '\n```\n\n';
      
      if (rec.improved_code) {
        markdown += '**Предлагаемый вариант:**\n\n';
        markdown += '```code\n' + rec.improved_code + '\n```\n\n';
      }
    });
    
    return markdown;
  };

  // Генерация Markdown для общего отчета
  const generateSummaryMarkdown = () => {
    return `
# Итоговый отчет анализа кода

${summary}

## Краткая сводка

- **Найдено багов**: ${bugs ? bugs.length : 0}
- **Найдено уязвимостей**: ${vulnerabilities ? vulnerabilities.length : 0}
- **Рекомендаций по улучшению**: ${recommendations ? recommendations.length : 0}
    `;
  };

  // Получение содержимого для текущей вкладки
  const getTabContent = () => {
    switch (activeTab) {
      case 0:
        return generateSummaryMarkdown();
      case 1:
        return generateMetricsMarkdown();
      case 2:
        return generateBugsMarkdown();
      case 3:
        return generateVulnerabilitiesMarkdown();
      case 4:
        return generateRecommendationsMarkdown();
      default:
        return '';
    }
  };

  // Компоненты для рендеринга Markdown
  const components = {
    code({ children, className }) {
      const language = className ? className.replace('language-', '') : 'javascript';
      return (
        <SyntaxHighlighter
          style={oneDark}
          language={language}
          showLineNumbers={true}
        >
          {children}
        </SyntaxHighlighter>
      );
    }
  };

  return (
    <Paper elevation={3} sx={{ mt: 4 }}>
      <Box p={3}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            mb: 2
          }}
        >
          <Tab label="Общий отчет" />
          <Tab label="Метрики" />
          <Tab label={`Баги (${bugs ? bugs.length : 0})`} />
          <Tab label={`Уязвимости (${vulnerabilities ? vulnerabilities.length : 0})`} />
          <Tab label={`Рекомендации (${recommendations ? recommendations.length : 0})`} />
        </Tabs>

        <Box className="markdown-content">
          <ReactMarkdown components={components}>
            {getTabContent()}
          </ReactMarkdown>
        </Box>
      </Box>
    </Paper>
  );
};

export default AnalysisReport; 