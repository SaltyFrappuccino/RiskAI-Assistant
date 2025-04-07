"""
Пакет содержит реализацию агентов для анализа кода.
"""
from agents.base_agent import CodeAnalysisAgent
from agents.code_requirements_agent import CodeRequirementsAgent
from agents.test_requirements_agent import TestRequirementsAgent
from agents.test_code_agent import TestCodeAgent
from agents.best_practices_agent import BestPracticesAgent
from agents.bug_detector_agent import BugDetectorAgent
from agents.vulnerability_detector_agent import VulnerabilityDetectorAgent
from agents.final_report_agent import FinalReportAgent
from agents.requirements_analyzer_agent import RequirementsAnalyzerAgent 