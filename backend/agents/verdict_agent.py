"""
Verdict Agent - Aggregate all agent outputs into a final signed verdict.

Inputs:
  - risk_analysis:       list of RiskDetection dicts from RiskDetectorAgent
  - compliance_issues:   list of ComplianceIssue dicts from ComplianceAgent
  - total_clauses:       int

Output: a single Verdict dict with:
  - risk_score (0-10)
  - verdict (DO_NOT_SIGN / SIGN_WITH_MODIFICATIONS / SAFE_TO_SIGN)
  - recommendation
  - rationale
  - top_issues (list[str])
  - negotiation_priorities (list[str])
  - executive_summary
"""

from typing import Any, Dict, List
from dataclasses import dataclass, asdict


@dataclass
class Verdict:
    risk_score: float
    verdict: str                        # VerdictClass value
    recommendation: str
    rationale: str
    critical_risks: int
    high_risks: int
    compliance_issues_critical: int
    compliance_issues_high: int
    top_issues: List[str]
    negotiation_priorities: List[str]
    executive_summary: str


class VerdictAgent:
    """
    Aggregate all agent outputs and produce a final verdict.

    Scoring formula (0-10):
      score = (critical_risks*10 + high_risks*7 + medium_risks*5
               + critical_compliance*8 + high_compliance*5) / max(total_clauses,1)
      capped at 10.

    Verdict thresholds:
      >= 8 OR >=3 critical risks OR >=2 critical compliance → DO NOT SIGN
      >= 5 OR >=3 high risks                                → SIGN WITH MODIFICATIONS
      otherwise                                             → SAFE TO SIGN
    """

    def generate_verdict(
        self,
        risk_analysis: List[Dict[str, Any]],
        compliance_issues: List[Dict[str, Any]],
        total_clauses: int,
    ) -> Dict[str, Any]:
        """
        Produce the final verdict dict.

        Args:
            risk_analysis:     flat list of risk dicts (each has 'risk_level', 'reason',
                               'clause_type', 'recommendation')
            compliance_issues: flat list of compliance issue dicts (each has 'severity',
                               'law_area', 'issue', 'recommendation')
            total_clauses:     number of parsed clauses

        Returns:
            Verdict as a plain dict.
        """
        # --- Count by severity ---
        critical_risks = sum(1 for r in risk_analysis if r.get("risk_level") == "CRITICAL")
        high_risks = sum(1 for r in risk_analysis if r.get("risk_level") == "HIGH")
        medium_risks = sum(1 for r in risk_analysis if r.get("risk_level") == "MEDIUM")

        critical_compliance = sum(
            1 for c in compliance_issues if c.get("severity") == "CRITICAL"
        )
        high_compliance = sum(
            1 for c in compliance_issues if c.get("severity") == "HIGH"
        )

        # --- Risk score ---
        raw_score = (
            critical_risks * 10
            + high_risks * 7
            + medium_risks * 5
            + critical_compliance * 8
            + high_compliance * 5
        ) / max(total_clauses, 1)
        risk_score = round(min(10.0, raw_score), 1)

        # --- Verdict class ---
        if risk_score >= 8 or critical_risks >= 1 or critical_compliance >= 2:
            verdict_class = "DO_NOT_SIGN"
            recommendation = (
                "Do NOT sign this contract. Critical issues must be resolved and "
                "redlined clauses negotiated before proceeding."
            )
        elif risk_score >= 5 or high_risks >= 3:
            verdict_class = "SIGN_WITH_MODIFICATIONS"
            recommendation = (
                "Do not sign as-is. Use the provided redlines to negotiate key terms "
                "before execution."
            )
        else:
            verdict_class = "SAFE_TO_SIGN"
            recommendation = (
                "Contract is relatively balanced. Review highlighted clauses and "
                "proceed with standard legal sign-off."
            )

        # --- Top issues (up to 5 most severe) ---
        top_issues = self._collect_top_issues(risk_analysis, compliance_issues)

        # --- Negotiation priorities ---
        negotiation_priorities = self._build_negotiation_priorities(
            risk_analysis, compliance_issues
        )

        # --- Rationale ---
        rationale = self._build_rationale(
            risk_score, critical_risks, high_risks, critical_compliance, high_compliance
        )

        # --- Executive summary ---
        executive_summary = (
            f"This contract scored {risk_score}/10 on risk. "
            f"Found {critical_risks} critical risk(s), {high_risks} high risk(s), "
            f"and {len(compliance_issues)} compliance gap(s). "
            f"Verdict: {verdict_class.replace('_', ' ')}. {recommendation}"
        )

        verdict = Verdict(
            risk_score=risk_score,
            verdict=verdict_class,
            recommendation=recommendation,
            rationale=rationale,
            critical_risks=critical_risks,
            high_risks=high_risks,
            compliance_issues_critical=critical_compliance,
            compliance_issues_high=high_compliance,
            top_issues=top_issues,
            negotiation_priorities=negotiation_priorities,
            executive_summary=executive_summary,
        )

        return asdict(verdict)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _collect_top_issues(
        self,
        risk_analysis: List[Dict[str, Any]],
        compliance_issues: List[Dict[str, Any]],
    ) -> List[str]:
        """Return up to 5 top issues ordered by severity."""
        issues: List[tuple] = []  # (sort_key, text)

        _risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "MINIMAL": 4}

        for r in risk_analysis:
            level = r.get("risk_level", "LOW")
            reason = r.get("reason", "")
            clause_type = r.get("clause_type", "")
            if level in ("CRITICAL", "HIGH"):
                issues.append(
                    (_risk_order.get(level, 9), f"[{level}] {clause_type}: {reason}")
                )

        for c in compliance_issues:
            sev = c.get("severity", "LOW")
            law = c.get("law_area", "")
            issue_txt = c.get("issue", "")
            if sev in ("CRITICAL", "HIGH"):
                issues.append(
                    (_risk_order.get(sev, 9), f"[{sev}] {law}: {issue_txt}")
                )

        issues.sort(key=lambda x: x[0])
        return [text for _, text in issues[:5]]

    def _build_negotiation_priorities(
        self,
        risk_analysis: List[Dict[str, Any]],
        compliance_issues: List[Dict[str, Any]],
    ) -> List[str]:
        """Build ordered list of negotiation actions."""
        priorities: List[str] = []

        for r in risk_analysis:
            rec = r.get("recommendation", "")
            level = r.get("risk_level", "")
            if rec and level in ("CRITICAL", "HIGH"):
                priorities.append(rec)

        for c in compliance_issues:
            rec = c.get("recommendation", "")
            sev = c.get("severity", "")
            if rec and sev in ("CRITICAL", "HIGH"):
                priorities.append(rec)

        # Deduplicate while preserving order
        seen = set()
        unique: List[str] = []
        for p in priorities:
            key = p[:80]
            if key not in seen:
                seen.add(key)
                unique.append(p)

        return unique[:6]  # cap at 6

    def _build_rationale(
        self,
        score: float,
        critical: int,
        high: int,
        compliance_critical: int,
        compliance_high: int,
    ) -> str:
        reasons: List[str] = []

        if critical > 0:
            reasons.append(
                f"{critical} critical risk clause(s) flagged — these pose severe "
                "legal or financial exposure and must be renegotiated."
            )
        if high > 0:
            reasons.append(
                f"{high} high-risk clause(s) identified — significant but negotiable risks."
            )
        if compliance_critical > 0:
            reasons.append(
                f"{compliance_critical} critical compliance gap(s) detected — "
                "potential IT Act / DPDP Act violations."
            )
        if compliance_high > 0:
            reasons.append(
                f"{compliance_high} high-severity compliance gap(s) — "
                "should be addressed before signing."
            )
        if not reasons:
            reasons.append(
                "No critical or high-severity issues found. Contract is relatively balanced."
            )

        return " ".join(reasons)
