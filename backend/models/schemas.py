from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContractUpload(BaseModel):
    filename: str
    path: str
    text_length: int
    chunks_count: int
    status: str

class RiskFlag(BaseModel):
    clause_number: str
    risk_level: RiskLevel
    description: str
    suggestion: Optional[str] = None

class AnalysisResult(BaseModel):
    contract_id: str
    risk_score: float
    verdict: str  # SIGN / SIGN_WITH_MODIFICATIONS / DONT_SIGN
    flagged_clauses: List[RiskFlag]
    compliance_issues: List[str]
    explanations: dict
