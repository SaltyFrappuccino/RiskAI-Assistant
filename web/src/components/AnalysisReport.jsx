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
  const processedData = analysisResult.processed_data || {};

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

${metrics.metrics_explanation ? '### Объяснение метрик\n\n' + metrics.metrics_explanation : ''}

${metrics.requirements_details ? '### Информация о требованиях\n\n' + metrics.requirements_details : ''}

${metrics.test_coverage_details ? '### Информация о покрытии тестами\n\n' + metrics.test_coverage_details : ''}
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
      if (bug.fix) {
        markdown += `**Решение проблемы**: ${bug.fix}\n\n`;
      }
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
      
      if (vuln.attack_vectors) {
        markdown += `**Возможные сценарии атак**: ${vuln.attack_vectors}\n\n`;
      }
      
      if (vuln.potential_impact) {
        markdown += `**Потенциальные последствия**: ${vuln.potential_impact}\n\n`;
      }
      
      markdown += `**Рекомендация по устранению**: ${vuln.mitigation}\n\n`;
    });
    
    return markdown;
  };

  // Генерация Markdown для требований
  const generateRequirementsMarkdown = () => {
    const satisfied = analysisResult.satisfied_requirements || [];
    const unsatisfied = analysisResult.unsatisfied_requirements || [];
    
    if (satisfied.length === 0 && unsatisfied.length === 0) {
      return '## Требования\n\nНет информации о требованиях.';
    }

    let markdown = '## Требования\n\n';
    
    if (satisfied.length > 0) {
      markdown += '### Выполненные требования\n\n';
      satisfied.forEach((req, index) => {
        markdown += `${index + 1}. ${req}\n`;
      });
      markdown += '\n';
    }
    
    if (unsatisfied.length > 0) {
      markdown += '### Невыполненные требования\n\n';
      unsatisfied.forEach((req, index) => {
        markdown += `${index + 1}. ${req}\n`;
      });
      markdown += '\n';
    }
    
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

  // Генерация Markdown для обработанных данных
  const generateProcessedDataMarkdown = () => {
    if (!processedData || Object.keys(processedData).length === 0) {
      return '## Данные после предобработки\n\nНет информации о предобработанных данных.';
    }

    // Если предобработка отключена
    if (processedData.preprocessing_disabled) {
      return '## Данные после предобработки\n\n⚠️ **Предобработка данных была отключена**\n\nДанные были использованы в исходном виде без предварительной обработки.';
    }

    let markdown = '## Данные после предобработки\n\n';
    
    if (processedData.story) {
      markdown += '### Story после обработки\n\n';
      markdown += '```\n' + processedData.story + '\n```\n\n';
    }
    
    if (processedData.requirements) {
      markdown += '### Требования после обработки\n\n';
      markdown += '```\n' + processedData.requirements + '\n```\n\n';
    }
    
    if (processedData.code) {
      markdown += '### Код после обработки\n\n';
      markdown += '```code\n' + processedData.code + '\n```\n\n';
    }
    
    if (processedData.test_cases) {
      markdown += '### Тест-кейсы после обработки\n\n';
      markdown += '```code\n' + processedData.test_cases + '\n```\n\n';
    }
    
    if (processedData.extreme_mode !== undefined) {
      markdown += `_Режим предобработки: ${processedData.extreme_mode ? 'Экстремальный' : 'Обычный'}_\n\n`;
    }
    
    return markdown;
  };

  // Генерация Markdown для общего отчета
  const generateSummaryMarkdown = () => {
    return `
# Итоговый отчет анализа кода

${summary}

## Краткая сводка

- **Соответствие кода требованиям**: ${metrics.code_requirements_match}%
- **Соответствие тест-кейсов требованиям**: ${metrics.test_requirements_match}%
- **Соответствие тест-кейсов коду**: ${metrics.test_code_match}%
- **Найдено багов**: ${bugs ? bugs.length : 0}
- **Найдено уязвимостей**: ${vulnerabilities ? vulnerabilities.length : 0}
- **Рекомендаций по улучшению**: ${recommendations ? recommendations.length : 0}

${metrics.metrics_explanation ? '### Объяснение метрик\n\n' + metrics.metrics_explanation : ''}

${generateRequirementsMarkdown()}

${bugs && bugs.length > 0 ? '## Критические проблемы\n\n' + 
  bugs.filter(bug => bug.severity === 'критический' || bug.severity === 'высокий')
    .map((bug, i) => `${i + 1}. **${bug.severity}**: ${bug.description.split('.')[0]}.\n`).join('') : ''}

${vulnerabilities && vulnerabilities.length > 0 ? '## Критические уязвимости\n\n' + 
  vulnerabilities.filter(vuln => vuln.severity === 'критическая' || vuln.severity === 'высокая')
    .map((vuln, i) => `${i + 1}. **${vuln.severity}**: ${vuln.description.split('.')[0]}.\n`).join('') : ''}
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
      case 5:
        return generateRequirementsMarkdown();
      case 6:
        return generateProcessedDataMarkdown();
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
          <Tab label="Требования" />
          <Tab label="Данные после обработки" />
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