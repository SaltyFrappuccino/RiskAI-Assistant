"""
Пакет содержит модели данных для приложения.
"""
from models.data_models import AnalysisRequest, AnalysisResult, Bug, Vulnerability, Recommendation, Metrics
from models.agent_schemas import (
    CodeRequirementsResult,
    TestRequirementsResult,
    TestCodeResult,
    BestPracticesResult,
    BugDetectorResult,
    VulnerabilityDetectorResult,
    FinalReportResult
) 