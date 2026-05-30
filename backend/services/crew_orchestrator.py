"""
Contract Analysis Orchestrator

Coordinates six agents in a direct Python pipeline:
  1. ParserAgent        â€“ extract and structure clauses
  2. RiskDetectorAgent  â€“ classify risks per clause
  3. ExplainerAgent     â€“ plain-English explanations
  4. RedlineAgent       â€“ safer clause rewrites (MEDIUM/HIGH/CRITICAL only)
  5. ComplianceAgent    â€“ Indian law & GDPR gap detection
  6. VerdictAgent       â€“ aggregate final verdict

No CrewAI runtime is used at the orchestration level; the pipeline calls each
agent directly and passes typed outputs forward.  CrewAI Agent/Task objects are
defined for documentation and future use when CrewAI stability improves.
"""

from typing import Any, Dict, List

from agents.parser_agent import ParserAgent
from agents.risk_detector_agent import RiskDetectorAgent
from agents.explainer_agent import ExplainerAgent
from agents.redline_agent import RedlineAgent
from agents.compliance_agent import ComplianceAgent
from agents.verdict_agent import VerdictAgent


# Risk levels that warrant a redline suggestion
_REDLINE_LEVELS = {"CRITICAL", "HIGH", "MEDIUM"}


class ContractAnalysisCrew:
    """
    Orchestrates all six contract analysis agents.

    Flow:
      extract text â†’ parse clauses â†’ detect risks â†’ explain â†’
      redline (filtered) â†’ compliance â†’ verdict â†’ compile response
    """

    def __init__(self) -> None:
        self.parser = ParserAgent()
        self.risk_detector = RiskDetectorAgent()
        self.explainer = ExplainerAgent()
        self.redline = RedlineAgent()
        self.compliance = ComplianceAgent()
        self.verdict_agent = VerdictAgent()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """
        Run the full six-agent pipeline and return a single typed response.

        Args:
            contract_text: Raw text of the contract (already extracted from PDF)

        Returns:
            Dict conforming to AnalysisResponse schema
        """

        # Step 1 â€“ Parse
        print("ðŸ“„ Step 1: Parsing contract...")
        parsed_clauses: List[Dict[str, Any]] = self.parser.parse_document(contract_text)

        if not parsed_clauses:
            return {"status": "error", "message": "Could not parse any clauses from contract"}

        print(f"   âœ“ {len(parsed_clauses)} clause(s) found")

        # Step 2 â€“ Detect risks
        print("âš ï¸  Step 2: Detecting risks...")
        risk_analysis: List[Dict[str, Any]] = self.risk_detector.detect_risks_batch(parsed_clauses)
        risk_summary = self.risk_detector.get_summary()
        print(f"   âœ“ Risk distribution: {risk_summary['risk_distribution']}")

        # Step 3 â€“ Explain
        print("ðŸ’¬ Step 3: Generating plain-English explanations...")
        explanations: List[Dict[str, Any]] = self.explainer.explain_clauses_batch(parsed_clauses)
        print(f"   âœ“ {len(explanations)} explanation(s) generated")

        # Step 4 â€“ Redlines (only for MEDIUM / HIGH / CRITICAL clauses)
        print("ðŸ”„ Step 4: Suggesting safer language for medium/high/critical clauses...")
        actionable_clauses, actionable_levels = self._filter_for_redlines(
            parsed_clauses, risk_analysis
        )
        redlines: List[Dict[str, Any]] = []
        if actionable_clauses:
            redlines = self.redline.suggest_redlines_batch(actionable_clauses, actionable_levels)
        print(f"   âœ“ {len(redlines)} redline suggestion(s) produced")

        # Step 5 â€“ Compliance
        print("[*] Step 5: Checking compliance...")
        compliance_issues: List[Dict[str, Any]] = self.compliance.check_compliance_batch(
            parsed_clauses
        )
        comp_summary = self.compliance.get_summary()
        print(f"   âœ“ {comp_summary['total_issues']} compliance issue(s) found")

        # Step 6 â€“ Verdict
        print("ðŸ“‹ Step 6: Generating final verdict...")
        verdict: Dict[str, Any] = self.verdict_agent.generate_verdict(
            risk_analysis, compliance_issues, len(parsed_clauses)
        )
        print(f"   âœ“ Verdict: {verdict['verdict']} (score {verdict['risk_score']}/10)")

        # Compile response
        high_risk_ids = [
            r["clause_id"]
            for r in risk_analysis
            if r.get("risk_level") in ("CRITICAL", "HIGH")
        ]

        return {
            "status": "success",
            "summary": {
                "total_clauses": len(parsed_clauses),
                "risk_distribution": risk_summary["risk_distribution"],
                "compliance_status": (
                    "COMPLIANT" if not compliance_issues else "NON-COMPLIANT"
                ),
                "high_risk_clause_ids": high_risk_ids,
            },
            "parsed_clauses": parsed_clauses,
            "risk_analysis": risk_analysis,
            "explanations": explanations,
            "redlines": redlines,
            "compliance_issues": compliance_issues,
            "verdict": verdict,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_for_redlines(
        parsed_clauses: List[Dict[str, Any]],
        risk_analysis: List[Dict[str, Any]],
    ):
        """
        Return only clauses whose detected risk level is MEDIUM, HIGH, or CRITICAL.

        Returns:
            Tuple of (filtered_clauses, corresponding_risk_levels)
        """
        risk_by_id: Dict[int, str] = {
            r["clause_id"]: r.get("risk_level", "MINIMAL") for r in risk_analysis
        }

        filtered_clauses: List[Dict[str, Any]] = []
        filtered_levels: List[str] = []

        for clause in parsed_clauses:
            cid = clause.get("clause_id", 0)
            level = risk_by_id.get(cid, "MINIMAL")
            if level in _REDLINE_LEVELS:
                filtered_clauses.append(clause)
                filtered_levels.append(level)

        return filtered_clauses, filtered_levels


def run_contract_analysis(contract_text: str) -> Dict[str, Any]:
    """
    Convenience wrapper â€“ run the full analysis pipeline.

    Args:
        contract_text: Extracted contract text

    Returns:
        Complete analysis dict
    """
    crew = ContractAnalysisCrew()
    return crew.analyze_contract(contract_text)
