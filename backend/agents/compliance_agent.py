"""Compliance Agent - Check contract clauses against Indian law and international standards"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ComplianceIssue:
    """Represents a detected compliance gap"""
    clause_id: int
    law_area: str       # e.g. "IT Act 2000", "GDPR", "Indian Contract Act"
    severity: Severity
    issue: str          # What is missing or wrong
    recommendation: str # What to add or change


class ComplianceAgent:
    """
    Detect compliance gaps in contract clauses against:
    - Indian IT Act 2000
    - Information Technology (Amendment) Act 2008
    - Indian Contract Act 1872
    - GDPR (for cross-border data flows)
    - PDPB / DPDP Act (India)
    - RBI guidelines (where relevant)

    Returns structured ComplianceIssue objects per clause.
    """

    # Compliance rule patterns: each rule has a law_area, severity,
    # keyword triggers (clause must be absent/present), issue text, and recommendation.
    RULES: List[Dict[str, Any]] = [
        # ---- Privacy & Data Protection ----
        {
            "law_area": "DPDP Act / GDPR",
            "severity": Severity.CRITICAL,
            "applies_to_types": ["general", "confidentiality", "compliance", "ip", "payment"],
            "require_keyword_absent": True,
            "keywords": [
                "personal data", "personal information", "data subject",
                "data protection", "privacy policy", "data controller",
                "data processor",
            ],
            "trigger_keyword": ["personal", "user data", "customer data", "employee data",
                                "pii", "personally identifiable"],
            "issue": "Clause processes personal data but contains no data protection obligations",
            "recommendation": (
                "Add: 'Any personal data processed under this Agreement shall comply with the "
                "Digital Personal Data Protection Act 2023 (India) and applicable GDPR requirements. "
                "The data processor shall implement appropriate technical and organisational measures "
                "to protect personal data.'"
            ),
        },
        {
            "law_area": "DPDP Act 2023",
            "severity": Severity.HIGH,
            "applies_to_types": ["general", "confidentiality", "compliance"],
            "require_keyword_absent": True,
            "keywords": ["consent", "explicit consent", "data principal consent"],
            "trigger_keyword": ["collect", "process", "store", "share", "personal data",
                                "user information"],
            "issue": "No consent mechanism defined for personal data collection or processing",
            "recommendation": (
                "Add a Consent clause: 'Data shall be collected only with explicit, informed, "
                "and freely given consent of the data principal. Consent may be withdrawn at any "
                "time, and the data fiduciary shall provide a mechanism to do so.'"
            ),
        },
        {
            "law_area": "DPDP Act 2023 / GDPR",
            "severity": Severity.HIGH,
            "applies_to_types": ["general", "confidentiality", "compliance"],
            "require_keyword_absent": True,
            "keywords": ["breach notification", "data breach", "notify", "72 hours",
                         "breach reporting"],
            "trigger_keyword": ["personal data", "user data", "data breach", "security incident"],
            "issue": "No data breach notification obligation specified",
            "recommendation": (
                "Add: 'In the event of a data breach, the data processor shall notify the data "
                "controller within 72 hours of becoming aware of the breach, including the nature "
                "of the breach, categories of data affected, and remediation steps taken.'"
            ),
        },
        # ---- IT Act 2000 ----
        {
            "law_area": "IT Act 2000 - S.43A",
            "severity": Severity.HIGH,
            "applies_to_types": ["confidentiality", "warranty", "compliance", "general"],
            "require_keyword_absent": True,
            "keywords": ["reasonable security", "security practices", "iso 27001",
                         "security standard", "information security"],
            "trigger_keyword": ["sensitive", "personal data", "confidential information",
                                "data", "information system"],
            "issue": "No reasonable security practices mandated as required by IT Act S.43A",
            "recommendation": (
                "Add: 'The parties shall implement and maintain reasonable security practices "
                "and procedures as required under Section 43A of the Information Technology Act 2000 "
                "and the Information Technology (Reasonable Security Practices) Rules 2011, "
                "including ISO 27001 or equivalent standards.'"
            ),
        },
        {
            "law_area": "IT Act 2000 - S.72A",
            "severity": Severity.CRITICAL,
            "applies_to_types": ["confidentiality", "compliance", "general"],
            "require_keyword_absent": True,
            "keywords": ["lawful purpose", "consent", "lawful contract", "lawfully obtained"],
            "trigger_keyword": ["disclose", "share", "personal information", "third party",
                                "transfer information"],
            "issue": (
                "Clause permits disclosure of personal information without restricting to "
                "lawful purposes (IT Act S.72A breach risk)"
            ),
            "recommendation": (
                "Add: 'Personal information shall only be disclosed for lawful purposes with "
                "the consent of the data principal or as required by law, in compliance with "
                "Section 72A of the Information Technology Act 2000.'"
            ),
        },
        # ---- Governing Law ----
        {
            "law_area": "Indian Contract Act 1872",
            "severity": Severity.MEDIUM,
            "applies_to_types": ["governing", "general"],
            "require_keyword_absent": True,
            "keywords": ["governing law", "jurisdiction", "applicable law",
                         "laws of india", "indian law"],
            "trigger_keyword": [],  # always check contracts missing governing law
            "issue": "No governing law or jurisdiction clause found",
            "recommendation": (
                "Add: 'This Agreement shall be governed by and construed in accordance with the "
                "laws of India. Any disputes shall be subject to the exclusive jurisdiction of "
                "courts in [City], India.'"
            ),
        },
        # ---- Cross-border Data Transfer ----
        {
            "law_area": "DPDP Act 2023 / IT Rules",
            "severity": Severity.HIGH,
            "applies_to_types": ["general", "confidentiality", "compliance", "ip"],
            "require_keyword_absent": True,
            "keywords": ["cross-border", "international transfer", "transfer outside india",
                         "standard contractual clauses", "adequacy decision"],
            "trigger_keyword": ["offshore", "overseas", "foreign jurisdiction", "outside india",
                                "international", "global"],
            "issue": "Cross-border data transfer occurs without adequate transfer safeguards",
            "recommendation": (
                "Add: 'Any transfer of personal data outside India shall comply with the "
                "Digital Personal Data Protection Act 2023 and applicable central government "
                "notifications on permissible countries. Standard contractual clauses or "
                "equivalent safeguards shall be in place.'"
            ),
        },
        # ---- Audit Rights ----
        {
            "law_area": "Indian Contract Act / IT Rules",
            "severity": Severity.MEDIUM,
            "applies_to_types": ["compliance", "confidentiality", "general"],
            "require_keyword_absent": True,
            "keywords": ["audit", "audit right", "right to audit", "inspection"],
            "trigger_keyword": ["service provider", "vendor", "processor", "sub-processor",
                                "data handling", "compliance"],
            "issue": "No audit rights reserved to verify compliance obligations",
            "recommendation": (
                "Add: 'Client shall have the right to audit the Service Provider's compliance "
                "with this Agreement upon 30 days written notice, or immediately in case of "
                "suspected breach, at Client's expense.'"
            ),
        },
        # ---- Subcontractor / Sub-processor ----
        {
            "law_area": "DPDP Act 2023 / Contract Law",
            "severity": Severity.MEDIUM,
            "applies_to_types": ["assignment", "general", "compliance"],
            "require_keyword_absent": True,
            "keywords": ["subcontractor", "sub-processor", "third party processor",
                         "subprocessor approval"],
            "trigger_keyword": ["subcontract", "sub-contract", "delegate", "outsource",
                                "third party service"],
            "issue": "No controls on sub-contractors or sub-processors who handle data",
            "recommendation": (
                "Add: 'Service Provider shall not engage sub-contractors to process personal data "
                "without prior written consent of the Client. Approved sub-contractors shall be "
                "bound by data protection obligations equivalent to those in this Agreement.'"
            ),
        },
        # ---- Limitation of liability without carve-out for data breaches ----
        {
            "law_area": "IT Act 2000 / DPDP Act",
            "severity": Severity.HIGH,
            "applies_to_types": ["liability", "limitation"],
            "require_keyword_absent": True,
            "keywords": ["data breach", "privacy breach", "information security breach"],
            "trigger_keyword": ["limitation of liability", "liability cap", "aggregate liability",
                                "maximum liability", "limit.*liability"],
            "issue": (
                "Liability cap applies without carve-out for data breach / privacy violations, "
                "which may be unenforceable under IT Act S.43A"
            ),
            "recommendation": (
                "Add a carve-out: 'The liability cap in this clause shall not apply to claims "
                "arising from a data breach caused by the Service Provider's negligence or "
                "wilful misconduct, or to penalties imposed under the IT Act / DPDP Act.'"
            ),
        },
    ]

    def __init__(self) -> None:
        self.issues: List[ComplianceIssue] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_compliance(self, clause: Dict[str, Any]) -> List[ComplianceIssue]:
        """
        Check a single clause for compliance gaps.

        Args:
            clause: dict with keys clause_id, clause_type, title, text

        Returns:
            List of ComplianceIssue objects (may be empty if compliant)
        """
        clause_id: int = clause.get("clause_id", 0)
        clause_type: str = clause.get("clause_type", "general")
        text: str = clause.get("text", "")
        text_lower = text.lower()

        issues: List[ComplianceIssue] = []

        for rule in self.RULES:
            # Check if this rule applies to this clause type
            if clause_type not in rule["applies_to_types"]:
                continue

            # Determine if trigger keywords fire (i.e. clause is relevant to the rule)
            trigger_kws: List[str] = rule.get("trigger_keyword", [])
            if trigger_kws:
                triggered = any(kw.lower() in text_lower for kw in trigger_kws)
                if not triggered:
                    continue

            # Determine if the protective keywords are ABSENT (that is the gap)
            protective_kws: List[str] = rule["keywords"]
            has_protection = any(kw.lower() in text_lower for kw in protective_kws)

            if rule["require_keyword_absent"] and not has_protection:
                issues.append(
                    ComplianceIssue(
                        clause_id=clause_id,
                        law_area=rule["law_area"],
                        severity=rule["severity"],
                        issue=rule["issue"],
                        recommendation=rule["recommendation"],
                    )
                )

        return issues

    def check_compliance_batch(
        self, clauses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check multiple clauses and return a flat list of all compliance issues.

        Args:
            clauses: List of clause dicts

        Returns:
            List of compliance issue dicts
        """
        self.issues = []
        results: List[Dict[str, Any]] = []

        for clause in clauses:
            clause_issues = self.check_compliance(clause)
            self.issues.extend(clause_issues)
            results.extend(asdict(issue) for issue in clause_issues)

        # Also run a document-level governing-law check if no governing clause found
        governing_types = {c.get("clause_type") for c in clauses}
        if "governing" not in governing_types:
            global_issue = ComplianceIssue(
                clause_id=0,
                law_area="Indian Contract Act 1872",
                severity=Severity.MEDIUM,
                issue="Contract has no governing law or jurisdiction clause",
                recommendation=(
                    "Add a Governing Law clause: 'This Agreement shall be governed by the laws "
                    "of India. Disputes shall be resolved before courts in [City], India.'"
                ),
            )
            self.issues.append(global_issue)
            results.append(asdict(global_issue))

        return results

    def get_summary(self) -> Dict[str, Any]:
        """Return counts by severity"""
        return {
            "total_issues": len(self.issues),
            "by_severity": {
                "CRITICAL": sum(1 for i in self.issues if i.severity == Severity.CRITICAL),
                "HIGH": sum(1 for i in self.issues if i.severity == Severity.HIGH),
                "MEDIUM": sum(1 for i in self.issues if i.severity == Severity.MEDIUM),
                "LOW": sum(1 for i in self.issues if i.severity == Severity.LOW),
            },
        }
