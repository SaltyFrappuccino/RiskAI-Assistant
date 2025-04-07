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
  useTheme,
  Badge
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
  const cacheStats = analysisResult.cache_stats || null;

  const hasCachedItems = Boolean(
    (bugs && bugs.some(bug => bug.from_cache)) ||
    (vulnerabilities && vulnerabilities.some(vuln => vuln.from_cache)) ||
    (recommendations && recommendations.some(rec => rec.from_cache))
  );

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

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

  const generateBugsMarkdown = () => {
    if (!bugs || bugs.length === 0) {
      return '## Баги\n\nБагов не обнаружено.';
    }

    let markdown = '## Найденные баги\n\n';
    
    const cachedBugs = bugs.filter(bug => bug.from_cache);
    const newBugs = bugs.filter(bug => !bug.from_cache);
    
    if (cachedBugs.length > 0) {
      markdown += `### ⚡ Найдено ${cachedBugs.length} баг(ов) в кэше\n\n`;
      
      cachedBugs.forEach((bug, index) => {
        markdown += `#### Баг ${index + 1} из кэша: ${bug.severity} приоритет\n\n`;
        markdown += `${bug.description}\n\n`;
        markdown += '```code\n' + bug.code_snippet + '\n```\n\n';
        if (bug.fix) {
          markdown += `**Решение проблемы**: ${bug.fix}\n\n`;
        }
      });
    }
    
    if (newBugs.length > 0) {
      if (cachedBugs.length > 0) {
        markdown += '### Новые баги\n\n';
      }
      
      newBugs.forEach((bug, index) => {
        markdown += `#### Баг ${index + 1}: ${bug.severity} приоритет\n\n`;
        markdown += `${bug.description}\n\n`;
        markdown += '```code\n' + bug.code_snippet + '\n```\n\n';
        if (bug.fix) {
          markdown += `**Решение проблемы**: ${bug.fix}\n\n`;
        }
      });
    }
    
    return markdown;
  };

  const generateVulnerabilitiesMarkdown = () => {
    if (!vulnerabilities || vulnerabilities.length === 0) {
      return '## Уязвимости\n\nУязвимостей не обнаружено.';
    }

    let markdown = '## Обнаруженные уязвимости\n\n';
    
    const cachedVulns = vulnerabilities.filter(vuln => vuln.from_cache);
    const newVulns = vulnerabilities.filter(vuln => !vuln.from_cache);
    
    if (cachedVulns.length > 0) {
      markdown += `### ⚡ Найдено ${cachedVulns.length} уязвимость(ей) в кэше\n\n`;
      
      cachedVulns.forEach((vuln, index) => {
        markdown += `#### Уязвимость ${index + 1} из кэша: ${vuln.severity} риск\n\n`;
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
    }
    
    if (newVulns.length > 0) {
      if (cachedVulns.length > 0) {
        markdown += '### Новые уязвимости\n\n';
      }
      
      newVulns.forEach((vuln, index) => {
        markdown += `#### Уязвимость ${index + 1}: ${vuln.severity} риск\n\n`;
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
    }
    
    return markdown;
  };

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

  const generateRecommendationsMarkdown = () => {
    if (!recommendations || recommendations.length === 0) {
      return '## Рекомендации\n\nРекомендаций нет.';
    }

    let markdown = '## Рекомендации по улучшению кода\n\n';
    
    const cachedRecs = recommendations.filter(rec => rec.from_cache);
    const newRecs = recommendations.filter(rec => !rec.from_cache);
    
    if (cachedRecs.length > 0) {
      markdown += `### ⚡ Найдено ${cachedRecs.length} рекомендаций в кэше\n\n`;
      
      cachedRecs.forEach((rec, index) => {
        markdown += `#### Рекомендация ${index + 1} из кэша\n\n`;
        markdown += `${rec.description}\n\n`;
        markdown += '**Текущий код:**\n\n';
        markdown += '```code\n' + rec.code_snippet + '\n```\n\n';
        
        if (rec.improved_code) {
          markdown += '**Предлагаемый вариант:**\n\n';
          markdown += '```code\n' + rec.improved_code + '\n```\n\n';
        }
        
        if (rec.reason) {
          markdown += `**Причина**: ${rec.reason}\n\n`;
        }
      });
    }
    
    if (newRecs.length > 0) {
      if (cachedRecs.length > 0) {
        markdown += '### Новые рекомендации\n\n';
      }
      
      newRecs.forEach((rec, index) => {
        markdown += `#### Рекомендация ${index + 1}\n\n`;
        markdown += `${rec.description}\n\n`;
        markdown += '**Текущий код:**\n\n';
        markdown += '```code\n' + rec.code_snippet + '\n```\n\n';
        
        if (rec.improved_code) {
          markdown += '**Предлагаемый вариант:**\n\n';
          markdown += '```code\n' + rec.improved_code + '\n```\n\n';
        }
        
        if (rec.reason) {
          markdown += `**Причина**: ${rec.reason}\n\n`;
        }
      });
    }
    
    return markdown;
  };

  const generateProcessedDataMarkdown = () => {
    if (!processedData || Object.keys(processedData).length === 0) {
      return '## Данные после предобработки\n\nНет информации о предобработанных данных.';
    }

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
  
  const generateCacheStatsMarkdown = () => {
    if (!cacheStats) {
      return '## Статистика кэша\n\nИнформация о кэше недоступна или кэширование отключено.';
    }
    
    let markdown = '## Статистика использования кэша\n\n';
    
    if (cacheStats.cache_usage_summary) {
      markdown += `### Сводка\n\n${cacheStats.cache_usage_summary}\n\n`;
    } else {
      const hitRate = cacheStats.cache_hits + cacheStats.cache_misses > 0 
        ? ((cacheStats.cache_hits / (cacheStats.cache_hits + cacheStats.cache_misses)) * 100).toFixed(2) 
        : 0;
        
      markdown += `### Сводка\n\n`;
      markdown += `- **Всего запросов к кэшу**: ${cacheStats.cache_hits + cacheStats.cache_misses}\n`;
      markdown += `- **Найдено в кэше**: ${cacheStats.cache_hits}\n`;
      markdown += `- **Не найдено в кэше**: ${cacheStats.cache_misses}\n`;
      markdown += `- **Добавлено в кэш**: ${cacheStats.cache_saves}\n`;
      markdown += `- **Эффективность кэша**: ${hitRate}%\n\n`;
    }
    
    if (cacheStats.cached_bugs && cacheStats.cached_bugs.length > 0) {
      markdown += `### Найденные в кэше баги\n\n`;
      cacheStats.cached_bugs.forEach((bugId, index) => {
        markdown += `${index + 1}. \`${bugId}\`\n`;
      });
      markdown += '\n';
    }
    
    if (cacheStats.cached_vulnerabilities && cacheStats.cached_vulnerabilities.length > 0) {
      markdown += `### Найденные в кэше уязвимости\n\n`;
      cacheStats.cached_vulnerabilities.forEach((vulnId, index) => {
        markdown += `${index + 1}. \`${vulnId}\`\n`;
      });
      markdown += '\n';
    }
    
    if (cacheStats.cached_recommendations && cacheStats.cached_recommendations.length > 0) {
      markdown += `### Найденные в кэше рекомендации\n\n`;
      cacheStats.cached_recommendations.forEach((recId, index) => {
        markdown += `${index + 1}. \`${recId}\`\n`;
      });
      markdown += '\n';
    }
    
    return markdown;
  };

  const generateSummaryMarkdown = () => {
    const cacheInfo = hasCachedItems 
      ? `\n\n⚡ **Использовались данные из кэша**: Некоторые результаты анализа были получены из кэша, что ускорило обработку.` 
      : '';
      
    return `
# Итоговый отчет анализа кода

${summary}${cacheInfo}

## Краткая сводка

- **Соответствие кода требованиям**: ${metrics.code_requirements_match}%
- **Соответствие тест-кейсов требованиям**: ${metrics.test_requirements_match}%
- **Соответствие тест-кейсов коду**: ${metrics.test_code_match}%
- **Найдено багов**: ${bugs ? bugs.length : 0}${bugs && bugs.some(b => b.from_cache) ? ' (есть из кэша)' : ''}
- **Найдено уязвимостей**: ${vulnerabilities ? vulnerabilities.length : 0}${vulnerabilities && vulnerabilities.some(v => v.from_cache) ? ' (есть из кэша)' : ''}
- **Рекомендаций по улучшению**: ${recommendations ? recommendations.length : 0}${recommendations && recommendations.some(r => r.from_cache) ? ' (есть из кэша)' : ''}

${metrics.metrics_explanation ? '### Объяснение метрик\n\n' + metrics.metrics_explanation : ''}

${generateRequirementsMarkdown()}

${bugs && bugs.length > 0 ? '## Критические проблемы\n\n' + 
  bugs.filter(bug => bug.severity === 'критический' || bug.severity === 'высокий')
    .map((bug, i) => `${i + 1}. **${bug.severity}**: ${bug.description.split('.')[0]}.${bug.from_cache ? ' (из кэша)' : ''}\n`).join('') : ''}

${vulnerabilities && vulnerabilities.length > 0 ? '## Критические уязвимости\n\n' + 
  vulnerabilities.filter(vuln => vuln.severity === 'критическая' || vuln.severity === 'высокая')
    .map((vuln, i) => `${i + 1}. **${vuln.severity}**: ${vuln.description.split('.')[0]}.${vuln.from_cache ? ' (из кэша)' : ''}\n`).join('') : ''}
    `;
  };

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
      case 7:
        return generateCacheStatsMarkdown();
      default:
        return '';
    }
  };

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
          <Tab 
            label={
              <Badge color="primary" badgeContent={bugs?.filter(bug => bug.from_cache).length || 0} 
                     showZero={false} max={999}>
                {`Баги (${bugs ? bugs.length : 0})`}
              </Badge>
            } 
          />
          <Tab 
            label={
              <Badge color="primary" badgeContent={vulnerabilities?.filter(vuln => vuln.from_cache).length || 0} 
                     showZero={false} max={999}>
                {`Уязвимости (${vulnerabilities ? vulnerabilities.length : 0})`}
              </Badge>
            }
          />
          <Tab 
            label={
              <Badge color="primary" badgeContent={recommendations?.filter(rec => rec.from_cache).length || 0} 
                     showZero={false} max={999}>
                {`Рекомендации (${recommendations ? recommendations.length : 0})`}
              </Badge>
            }
          />
          <Tab label="Требования" />
          <Tab label="Данные после обработки" />
          {cacheStats && (
            <Tab 
              label={
                <Box display="flex" alignItems="center">
                  <span style={{ marginRight: '4px', fontSize: '16px' }}>💾</span>
                  Кэш
                </Box>
              }
            />
          )}
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