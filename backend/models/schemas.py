from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Shared enumerations
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    """Risk severity – uppercase to match agent outputs."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class VerdictClass(str, Enum):
    DO_NOT_SIGN = "DO_NOT_SIGN"
    SIGN_WITH_MODIFICATIONS = "SIGN_WITH_MODIFICATIONS"
    SAFE_TO_SIGN = "SAFE_TO_SIGN"


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class ContractUpload(BaseModel):
    filename: str
    path: str
    text_length: int
    chunks_count: int
    status: str


# ---------------------------------------------------------------------------
# Parsed clause
# ---------------------------------------------------------------------------

class Clause(BaseModel):
    clause_id: int
    clause_number: str
    clause_type: str
    title: str
    text: str
    section: str


# ---------------------------------------------------------------------------
# Risk detection
# ---------------------------------------------------------------------------

class RiskFlag(BaseModel):
    clause_id: int
    clause_type: str
    risk_level: RiskLevel
    reason: str
    keywords_found: List[str] = Field(default_factory=list)
    recommendation: str


# ---------------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------------

class ClauseExplanation(BaseModel):
    clause_id: int
    clause_type: str
    original_text: str
    simple_explanation: str
    key_terms: Dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Redline suggestion
# ---------------------------------------------------------------------------

class RedlineSuggestion(BaseModel):
    clause_id: int
    clause_type: str
    risk_level: str
    original_clause: str
    suggested_clause: str
    reasoning: str
    key_changes: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Compliance issue
# ---------------------------------------------------------------------------

class ComplianceIssue(BaseModel):
    clause_id: int
    law_area: str
    severity: RiskLevel
    issue: str
    recommendation: str


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

class Verdict(BaseModel):
    risk_score: float = Field(..., ge=0, le=10)
    verdict: VerdictClass
    recommendation: str
    rationale: str
    critical_risks: int = 0
    high_risks: int = 0
    compliance_issues_critical: int = 0
    compliance_issues_high: int = 0
    top_issues: List[str] = Field(default_factory=list)
    negotiation_priorities: List[str] = Field(default_factory=list)
    executive_summary: str = ""


# ---------------------------------------------------------------------------
# Summary block
# ---------------------------------------------------------------------------

class AnalysisSummary(BaseModel):
    total_clauses: int
    risk_distribution: Dict[str, int]
    compliance_status: str   # "COMPLIANT" | "NON-COMPLIANT"
    high_risk_clause_ids: List[int] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level analysis response
# ---------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    status: str = "success"
    summary: AnalysisSummary
    parsed_clauses: List[Dict[str, Any]] = Field(default_factory=list)
    risk_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    explanations: List[Dict[str, Any]] = Field(default_factory=list)
    redlines: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_issues: List[Dict[str, Any]] = Field(default_factory=list)
    verdict: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class TextAnalysisRequest(BaseModel):
    text: str
