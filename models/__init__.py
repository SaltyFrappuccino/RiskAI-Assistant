"""
Пакет содержит модели данных для приложения.
"""
from models.data_models import (
    AnalysisRequest, 
    AnalysisResult, 
    Bug, 
    Vulnerability, 
    Recommendation, 
    Metrics,
    RequirementsAnalysisRequest,
    RequirementsAnalysisResult
)
from models.agent_schemas import (
    CodeRequirementsResult,
    TestRequirementsResult,
    TestCodeResult,
    BestPracticesResult,
    BugDetectorResult,
    VulnerabilityDetectorResult,
    FinalReportResult,
    RequirementsAnalyzerResult
) 