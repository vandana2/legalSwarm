"""
LegalSwarm – Multi-Agent Test Suite

Tests each agent in isolation and the full pipeline end-to-end.

Usage:
    python test_parser.py                        # run all tests
    python test_parser.py --file path/to/NDA.pdf # also test a real PDF
    python test_parser.py --list                 # list available sample contracts
"""

import argparse
import json
import os
import sys
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from agents.parser_agent import ParserAgent
from agents.risk_detector_agent import RiskDetectorAgent
from agents.explainer_agent import ExplainerAgent
from agents.redline_agent import RedlineAgent
from agents.compliance_agent import ComplianceAgent
from agents.verdict_agent import VerdictAgent
from services.pdf_parser import PDFParser
from services.crew_orchestrator import run_contract_analysis


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sep(title: str = "") -> None:
    if title:
        print(f"\n{'='*78}\n  {title}\n{'='*78}\n")
    else:
        print(f"\n{'-'*78}\n")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def fail(msg: str) -> None:
    print(f"  ✗ FAIL: {msg}")


def assert_true(condition: bool, msg: str) -> bool:
    if condition:
        ok(msg)
        return True
    fail(msg)
    return False


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_CONTRACT = """
Section 1: Liability
The Company shall not be liable for any indirect, incidental, or consequential
damages. The total liability shall not exceed the fees paid in the last 12 months.

Section 2: Termination
Either party may terminate this agreement immediately without cause and without
notice at any time.

Section 3: Confidentiality
Each party agrees to maintain confidentiality of proprietary information in
perpetuity. Confidential information shall never be disclosed to third parties.

Section 4: Payment
All fees are strictly non-refundable under any circumstances. Late payments will
incur interest at 3% per month.

Section 5: Intellectual Property
All work product, inventions, and intellectual property created during the term
of this agreement shall be assigned to and owned by the Company.

Section 6: Auto-Renewal
This agreement will renew automatically unless cancelled in writing 90 days
prior to the renewal date.

Section 7: Personal Data
The Service Provider will collect, process, and share customer personal data and
user information with third-party offshore services.
"""

RISKY_CLAUSE = {
    "clause_id": 1,
    "clause_type": "liability",
    "title": "Unlimited Liability",
    "text": "The vendor is liable for all damages without any limitation.",
    "section": "Section 1",
    "clause_number": "1",
}

RENEWAL_CLAUSE = {
    "clause_id": 2,
    "clause_type": "renewal",
    "title": "Auto-Renewal",
    "text": "This contract renews automatically unless cancelled in writing 90 days prior.",
    "section": "Section 6",
    "clause_number": "6",
}

SAFE_CLAUSE = {
    "clause_id": 3,
    "clause_type": "payment",
    "title": "Payment Terms",
    "text": "Payment is due within 30 days of invoice date.",
    "section": "Section 4",
    "clause_number": "4",
}

DATA_CLAUSE = {
    "clause_id": 4,
    "clause_type": "general",
    "title": "Data Handling",
    "text": (
        "The Service Provider will collect and process customer personal data "
        "and share user information with third-party offshore services."
    ),
    "section": "Section 7",
    "clause_number": "7",
}


# ---------------------------------------------------------------------------
# Individual agent tests
# ---------------------------------------------------------------------------

def test_parser() -> bool:
    sep("TEST: ParserAgent – clause extraction")
    passed = True

    parser = ParserAgent()
    clauses = parser.parse_document(SAMPLE_CONTRACT)

    passed &= assert_true(len(clauses) > 0, f"Extracted {len(clauses)} clause(s)")
    passed &= assert_true(
        any(c["clause_type"] == "liability" for c in clauses),
        "Identified at least one 'liability' clause",
    )
    passed &= assert_true(
        any(c["clause_type"] == "termination" for c in clauses),
        "Identified at least one 'termination' clause",
    )
    passed &= assert_true(
        all("clause_id" in c and "text" in c and "clause_type" in c for c in clauses),
        "All clauses have required fields (clause_id, text, clause_type)",
    )

    summary = parser.get_summary()
    ok(f"Clause type distribution: {summary['clause_types']}")
    return passed


def test_risk_detector() -> bool:
    sep("TEST: RiskDetectorAgent – risk classification")
    passed = True

    agent = RiskDetectorAgent()
    risky = agent.detect_risks(RISKY_CLAUSE)
    passed &= assert_true(
        risky["risk_level"] in ("CRITICAL", "HIGH"),
        f"Unlimited liability clause classified as {risky['risk_level']} (expected CRITICAL/HIGH)",
    )

    agent2 = RiskDetectorAgent()
    renewal = agent2.detect_risks(RENEWAL_CLAUSE)
    passed &= assert_true(
        renewal["risk_level"] in ("CRITICAL", "HIGH", "MEDIUM"),
        f"Auto-renewal clause classified as {renewal['risk_level']} (expected >= MEDIUM)",
    )

    agent3 = RiskDetectorAgent()
    safe = agent3.detect_risks(SAFE_CLAUSE)
    passed &= assert_true(
        safe["risk_level"] in ("LOW", "MINIMAL"),
        f"Safe payment clause classified as {safe['risk_level']} (expected LOW/MINIMAL)",
    )

    return passed


def test_explainer() -> bool:
    sep("TEST: ExplainerAgent – plain-English explanations")
    passed = True

    agent = ExplainerAgent()
    explanations = agent.explain_clauses_batch([RISKY_CLAUSE, SAFE_CLAUSE])

    passed &= assert_true(len(explanations) == 2, "Got 2 explanations for 2 input clauses")
    passed &= assert_true(
        all("simple_explanation" in e and e["simple_explanation"] for e in explanations),
        "Each explanation has a non-empty simple_explanation field",
    )
    passed &= assert_true(
        all("key_terms" in e for e in explanations),
        "Each explanation has a key_terms field",
    )
    return passed


def test_redline() -> bool:
    sep("TEST: RedlineAgent – safer clause rewrites")
    passed = True

    agent = RedlineAgent()
    redline = agent.suggest_redline(RISKY_CLAUSE, "CRITICAL")
    passed &= assert_true(
        bool(redline["suggested_clause"]),
        "Produced a non-empty suggested_clause for CRITICAL risk",
    )
    passed &= assert_true(
        bool(redline["reasoning"]),
        "Produced a non-empty reasoning",
    )

    results = agent.suggest_redlines_batch(
        [RISKY_CLAUSE, RENEWAL_CLAUSE], ["CRITICAL", "HIGH"]
    )
    passed &= assert_true(len(results) == 2, f"Batch produced {len(results)} redline(s)")
    return passed


def test_compliance_agent() -> bool:
    sep("TEST: ComplianceAgent – Indian law & GDPR gaps")
    passed = True

    agent = ComplianceAgent()
    issues = agent.check_compliance(DATA_CLAUSE)
    passed &= assert_true(
        len(issues) > 0,
        f"Data-handling clause flagged {len(issues)} compliance issue(s) (expected ≥1)",
    )
    passed &= assert_true(
        all(hasattr(i, "law_area") and hasattr(i, "severity") for i in issues),
        "All issues have law_area and severity",
    )

    all_issues = agent.check_compliance_batch(
        [RISKY_CLAUSE, RENEWAL_CLAUSE, SAFE_CLAUSE, DATA_CLAUSE]
    )
    passed &= assert_true(
        len(all_issues) > 0,
        f"Batch found {len(all_issues)} total compliance issue(s)",
    )

    summary = agent.get_summary()
    ok(f"Compliance summary: {summary}")
    return passed


def test_verdict_agent() -> bool:
    sep("TEST: VerdictAgent – final aggregation")
    passed = True

    agent = VerdictAgent()

    mock_risks = [
        {"clause_id": 1, "risk_level": "CRITICAL", "reason": "Unlimited liability",
         "clause_type": "liability", "recommendation": "Cap liability"},
        {"clause_id": 2, "risk_level": "HIGH", "reason": "Auto-renewal trap",
         "clause_type": "renewal", "recommendation": "Remove auto-renewal"},
        {"clause_id": 3, "risk_level": "HIGH", "reason": "IP assignment",
         "clause_type": "ip", "recommendation": "Retain IP rights"},
    ]
    mock_compliance = [
        {"clause_id": 4, "severity": "CRITICAL", "law_area": "IT Act 2000",
         "issue": "No security practices", "recommendation": "Add ISO 27001"},
    ]

    verdict = agent.generate_verdict(mock_risks, mock_compliance, total_clauses=5)

    passed &= assert_true("risk_score" in verdict, "Verdict has risk_score")
    passed &= assert_true(
        verdict["verdict"] in ("DO_NOT_SIGN", "SIGN_WITH_MODIFICATIONS", "SAFE_TO_SIGN"),
        f"Verdict class is valid: {verdict['verdict']}",
    )
    passed &= assert_true(
        verdict["verdict"] == "DO_NOT_SIGN",
        "1 CRITICAL + 2 HIGH risks → verdict is DO_NOT_SIGN",
    )
    passed &= assert_true(len(verdict["top_issues"]) > 0, "top_issues is populated")
    passed &= assert_true(bool(verdict["executive_summary"]), "executive_summary is non-empty")

    ok(f"Risk score: {verdict['risk_score']}/10  Verdict: {verdict['verdict']}")
    return passed


def test_full_pipeline() -> bool:
    sep("TEST: Full Pipeline – end-to-end orchestration")
    passed = True

    result = run_contract_analysis(SAMPLE_CONTRACT)

    passed &= assert_true(result["status"] == "success", "Pipeline returned status=success")
    passed &= assert_true("summary" in result, "Response has 'summary'")
    passed &= assert_true("parsed_clauses" in result, "Response has 'parsed_clauses'")
    passed &= assert_true("risk_analysis" in result, "Response has 'risk_analysis'")
    passed &= assert_true("explanations" in result, "Response has 'explanations'")
    passed &= assert_true("redlines" in result, "Response has 'redlines'")
    passed &= assert_true("compliance_issues" in result, "Response has 'compliance_issues'")
    passed &= assert_true("verdict" in result, "Response has 'verdict'")

    risk_by_id = {r["clause_id"]: r["risk_level"] for r in result["risk_analysis"]}
    for redline in result["redlines"]:
        cid = redline.get("clause_id")
        level = risk_by_id.get(cid, "MINIMAL")
        passed &= assert_true(
            level in ("MEDIUM", "HIGH", "CRITICAL"),
            f"Redline for clause {cid} has level {level} (must be ≥ MEDIUM)",
        )

    verdict = result["verdict"]
    passed &= assert_true(
        isinstance(verdict.get("risk_score"), float),
        f"Verdict risk_score is a float: {verdict.get('risk_score')}",
    )

    ok(
        f"Clauses: {result['summary']['total_clauses']}  "
        f"Redlines: {len(result['redlines'])}  "
        f"Compliance issues: {len(result['compliance_issues'])}  "
        f"Verdict: {verdict.get('verdict')}  Score: {verdict.get('risk_score')}/10"
    )
    return passed


# ---------------------------------------------------------------------------
# PDF / utility helpers
# ---------------------------------------------------------------------------

def test_parser_with_text(text: str, title: str = "Test Contract") -> list:
    sep(f"Parser test: {title}")
    parser = ParserAgent()
    clauses = parser.parse_document(text)
    ok(f"Total clauses found: {len(clauses)}")
    summary = parser.get_summary()
    print("  Clause types:", summary["clause_types"])
    for i, clause in enumerate(clauses[:5], 1):
        print(f"\n  Clause #{i}: [{clause['clause_type']}] {clause['title']}")
        print(f"  {clause['text'][:120]}...")
    if len(clauses) > 5:
        print(f"\n  … and {len(clauses) - 5} more")
    return clauses


def test_parser_with_pdf(pdf_path: str) -> list:
    sep(f"PDF test: {pdf_path}")
    if not os.path.exists(pdf_path):
        fail(f"File not found: {pdf_path}")
        return []
    try:
        pdf_parser = PDFParser(pdf_path)
        text = pdf_parser.extract_text()
        ok(f"Extracted {len(text)} characters from PDF")
        return test_parser_with_text(text, Path(pdf_path).name)
    except Exception as exc:
        fail(str(exc))
        return []


def list_sample_contracts() -> list:
    sample_dir = "docs/sample_contracts"
    if not os.path.exists(sample_dir):
        print(f"Sample contracts directory not found: {sample_dir}")
        return []
    pdf_files = list(Path(sample_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {sample_dir}")
        return []
    print(f"\nFound {len(pdf_files)} sample contract(s):")
    for i, p in enumerate(pdf_files, 1):
        print(f"  {i}. {p.name} ({os.path.getsize(p)/1024:.1f} KB)")
    return pdf_files


def save_results_to_json(data: object, output_file: str = "test_results.json") -> None:
    with open(output_file, "w") as fh:
        json.dump(data, fh, indent=2, default=str)
    ok(f"Results saved to: {output_file}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="LegalSwarm multi-agent test suite"
    )
    arg_parser.add_argument("--file", type=str, help="Path to a PDF to test")
    arg_parser.add_argument("--list", action="store_true", help="List sample contracts")
    args = arg_parser.parse_args()

    sep("LegalSwarm – Multi-Agent Test Suite")

    results = {
        "parser":     test_parser(),
        "risk":       test_risk_detector(),
        "explainer":  test_explainer(),
        "redline":    test_redline(),
        "compliance": test_compliance_agent(),
        "verdict":    test_verdict_agent(),
        "pipeline":   test_full_pipeline(),
    }

    sep("RESULTS")
    total = len(results)
    passed = sum(results.values())
    for name, ok_flag in results.items():
        status = "PASS" if ok_flag else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\n  {passed}/{total} test groups passed\n")

    if args.list:
        list_sample_contracts()

    if args.file:
        clauses = test_parser_with_pdf(args.file)
        if clauses:
            save_results_to_json(clauses, f"test_results_{Path(args.file).stem}.json")


if __name__ == "__main__":
    main()