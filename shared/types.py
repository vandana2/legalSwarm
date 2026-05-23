from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class Verdict(str, Enum):
    SIGN = "SIGN"
    SIGN_WITH_MODIFICATIONS = "SIGN_WITH_MODIFICATIONS"
    DONT_SIGN = "DONT_SIGN"

@dataclass
class FlaggedClause:
    clause_number: str
    risk_level: RiskLevel
    description: str
    suggestion: Optional[str] = None

@dataclass
class AnalysisReport:
    contract_id: str
    risk_score: float
    verdict: Verdict
    flagged_clauses: List[FlaggedClause]
    compliance_issues: List[str]
    analysis_time: float
