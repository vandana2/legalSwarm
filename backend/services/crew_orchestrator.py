"""
CrewAI Orchestration - Coordinates all agents for contract analysis
Uses CrewAI to run agents in parallel and generate final verdict
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict, List, Any
from agents.parser_agent import ParserAgent
from agents.risk_detector_agent import RiskDetectorAgent
from agents.explainer_agent import ExplainerAgent
from agents.redline_agent import RedlineAgent
from agents.compliance_agent import ComplianceAgent
import json


class ContractAnalysisCrew:
    """
    Orchestrates all contract analysis agents using CrewAI
    
    Flow:
    1. Parser Agent - Extracts clauses
    2. Risk Detector Agent - Identifies risks
    3. Explainer Agent - Translates to plain English
    4. Redline Agent - Suggests better language
    5. Compliance Agent - Checks laws
    6. Verdict Agent - Final scoring & recommendation
    """
    
    def __init__(self):
        self.parser = ParserAgent()
        self.risk_detector = RiskDetectorAgent()
        self.explainer = ExplainerAgent()
        self.redline = RedlineAgent()
        self.compliance = ComplianceAgent()
    
    def setup_agents(self) -> Dict[str, Agent]:
        """Setup CrewAI agents"""
        
        agents = {
            'parser': Agent(
                role='Legal Document Parser',
                goal='Extract and structure clauses from contract PDFs',
                backstory='Expert at identifying and categorizing legal clauses',
                verbose=True
            ),
            'risk_detector': Agent(
                role='Legal Risk Analyzer',
                goal='Identify financial and legal risks in contract clauses',
                backstory='Specialized in spotting unfair and risky contract terms',
                verbose=True
            ),
            'explainer': Agent(
                role='Legal Language Translator',
                goal='Convert complex legal jargon into simple, understandable English',
                backstory='Makes legal documents accessible to business professionals',
                verbose=True
            ),
            'redline': Agent(
                role='Contract Negotiation Specialist',
                goal='Suggest safer, more balanced alternative language for risky clauses',
                backstory='Expert negotiator with 20+ years of contract experience',
                verbose=True
            ),
            'compliance': Agent(
                role='Compliance & Legal Advisor',
                goal='Ensure contract complies with Indian IT Act, GDPR, and data privacy laws',
                backstory='Specialist in Indian law and international compliance standards',
                verbose=True
            ),
            'verdict': Agent(
                role='Contract Verdict Specialist',
                goal='Generate final risk score, summary, and recommendation',
                backstory='Synthesizes all analysis into actionable guidance',
                verbose=True
            )
        }
        
        return agents
    
    def setup_tasks(self, agents: Dict[str, Agent], contract_text: str) -> List[Task]:
        """Setup tasks for each agent"""
        
        tasks = [
            Task(
                description=f'''Parse and structure the following contract:
                {contract_text[:1000]}...
                
                Extract all clauses and categorize them by type (liability, termination, confidentiality, IP, payment, etc.)
                Output structured JSON with clause_id, clause_type, title, and text.''',
                agent=agents['parser'],
                expected_output='Structured JSON list of clauses'
            ),
            
            Task(
                description='''Analyze each parsed clause for legal and financial risks.
                Identify:
                - Unlimited liability clauses
                - Auto-renewal traps
                - Unfair IP assignment
                - Unreasonable termination terms
                - Non-refundable payment risks
                
                Rate each clause as CRITICAL, HIGH, MEDIUM, or LOW risk.
                Provide specific reasoning for each risk.''',
                agent=agents['risk_detector'],
                expected_output='Risk assessment for all clauses with severity levels'
            ),
            
            Task(
                description='''Translate legal jargon in all clauses to plain English.
                For each clause:
                - Explain what it means
                - Define key legal terms
                - Provide plain language summary
                
                Make the analysis accessible to business professionals without legal training.''',
                agent=agents['explainer'],
                expected_output='Plain English explanations for all clauses'
            ),
            
            Task(
                description='''For risky clauses, suggest safer alternative language that:
                - Protects the client
                - Remains fair to both parties
                - Follows legal best practices
                
                Provide original clause, suggested revision, and key changes.''',
                agent=agents['redline'],
                expected_output='Redline suggestions for high-risk clauses'
            ),
            
            Task(
                description='''Check all clauses for compliance with:
                - Indian IT Act 2000
                - GDPR and data protection requirements
                - Indian Contract Act 1872
                - Data privacy standards
                
                Identify any compliance violations or gaps.
                Rate severity (CRITICAL, HIGH, MEDIUM).''',
                agent=agents['compliance'],
                expected_output='Compliance assessment and recommendations'
            ),
            
            Task(
                description='''Based on all analysis, provide:
                1. Overall Risk Score (0-10)
                2. Verdict: DO NOT SIGN / SIGN WITH MODIFICATIONS / SAFE TO SIGN
                3. Top 3 Critical Issues
                4. Key recommendations for negotiation
                5. Estimated risk mitigation effort
                
                Synthesize all agent findings into actionable guidance.''',
                agent=agents['verdict'],
                expected_output='Final verdict with risk score and recommendations'
            )
        ]
        
        return tasks
    
    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """
        Run full contract analysis using CrewAI
        
        Args:
            contract_text: Full text of the contract
        
        Returns:
            Comprehensive analysis with all findings
        """
        
        # Step 1: Parse document
        print("📄 Step 1: Parsing contract...")
        parsed_clauses = self.parser.parse_document(contract_text)
        
        if not parsed_clauses:
            return {
                'status': 'error',
                'message': 'Could not parse contract'
            }
        
        print(f"✓ Found {len(parsed_clauses)} clauses\n")
        
        # Step 2: Detect risks
        print("⚠️ Step 2: Detecting risks...")
        risk_analysis = self.risk_detector.detect_risks_batch(parsed_clauses)
        print(f"✓ Risk analysis complete\n")
        
        # Step 3: Generate explanations
        print("💬 Step 3: Generating plain English explanations...")
        explanations = self.explainer.explain_clauses_batch(parsed_clauses)
        print(f"✓ Explanations complete\n")
        
        # Step 4: Generate redlines
        print("🔄 Step 4: Suggesting safer language...")
        risk_levels = [risk['risk_level'] for risk in risk_analysis]
        redlines = self.redline.suggest_redlines_batch(parsed_clauses, risk_levels)
        print(f"✓ Redlines complete\n")
        
        # Step 5: Check compliance
        print("🔐 Step 5: Checking compliance...")
        compliance_issues = self.compliance.check_compliance_batch(parsed_clauses)
        print(f"✓ Compliance check complete\n")
        
        # Step 6: Generate verdict
        print("📋 Step 6: Generating final verdict...")
        verdict = self._generate_verdict(risk_analysis, compliance_issues, len(parsed_clauses))
        print(f"✓ Verdict complete\n")
        
        # Compile all results
        result = {
            'status': 'success',
            'summary': {
                'total_clauses': len(parsed_clauses),
                'risk_distribution': self.risk_detector.get_summary()['risk_distribution'],
                'compliance_status': 'COMPLIANT' if not compliance_issues else 'NON-COMPLIANT'
            },
            'parsed_clauses': parsed_clauses,
            'risk_analysis': risk_analysis,
            'explanations': explanations,
            'redlines': redlines,
            'compliance_issues': compliance_issues,
            'verdict': verdict,
            'analysis_summary': self._create_analysis_summary(
                parsed_clauses, risk_analysis, compliance_issues, verdict
            )
        }
        
        return result
    
    def _generate_verdict(self, risks: List[Dict], compliance_issues: List[Dict], 
                         total_clauses: int) -> Dict[str, Any]:
        """Generate final verdict with scoring"""
        
        # Count risks by level
        critical_risks = sum(1 for r in risks if r['risk_level'] == 'CRITICAL')
        high_risks = sum(1 for r in risks if r['risk_level'] == 'HIGH')
        medium_risks = sum(1 for r in risks if r['risk_level'] == 'MEDIUM')
        
        # Count compliance issues by severity
        critical_compliance = sum(1 for c in compliance_issues if c.get('severity') == 'CRITICAL')
        high_compliance = sum(1 for c in compliance_issues if c.get('severity') == 'HIGH')
        
        # Calculate risk score (0-10)
        risk_score = (
            (critical_risks * 10 + high_risks * 7 + medium_risks * 5 + critical_compliance * 8 + high_compliance * 5)
            / max(total_clauses, 1)
        )
        risk_score = min(10, risk_score)  # Cap at 10
        
        # Determine verdict
        if risk_score >= 8 or critical_risks >= 3 or critical_compliance >= 2:
            verdict = "🔴 DO NOT SIGN"
            recommendation = "Critical issues must be resolved before signing"
        elif risk_score >= 6 or high_risks >= 3:
            verdict = "🟡 SIGN WITH MODIFICATIONS"
            recommendation = "Negotiate key terms before signing. Use provided redlines."
        else:
            verdict = "🟢 SAFE TO SIGN"
            recommendation = "Contract is relatively balanced. Standard review recommended."
        
        return {
            'risk_score': round(risk_score, 1),
            'verdict': verdict,
            'recommendation': recommendation,
            'critical_risks': critical_risks,
            'high_risks': high_risks,
            'compliance_issues_critical': critical_compliance,
            'compliance_issues_high': high_compliance,
            'rationale': self._get_verdict_rationale(
                risk_score, critical_risks, high_risks, critical_compliance
            )
        }
    
    def _get_verdict_rationale(self, score: float, critical: int, high: int, 
                              compliance_critical: int) -> str:
        """Generate rationale for verdict"""
        
        reasons = []
        
        if critical >= 2:
            reasons.append(f"• {critical} critical risk issues detected")
        if high >= 3:
            reasons.append(f"• {high} high-risk clauses that need negotiation")
        if compliance_critical >= 1:
            reasons.append(f"• {compliance_critical} critical compliance violations")
        
        if score >= 8:
            reasons.append("• Overall risk score is very high")
        elif score >= 6:
            reasons.append("• Multiple moderate to high risks present")
        
        return "\n".join(reasons) if reasons else "Contract terms are reasonable and standard."
    
    def _create_analysis_summary(self, clauses: List[Dict], risks: List[Dict], 
                                compliance_issues: List[Dict], verdict: Dict[str, Any]) -> str:
        """Create human-readable summary"""
        
        summary = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    CONTRACT ANALYSIS SUMMARY REPORT                        ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 DOCUMENT OVERVIEW:
   • Total Clauses: {len(clauses)}
   • Critical Risks: {verdict['critical_risks']}
   • High Risks: {verdict['high_risks']}
   • Compliance Issues: {verdict['compliance_issues_critical'] + verdict['compliance_issues_high']}

⚠️ RISK ASSESSMENT:
   • Overall Risk Score: {verdict['risk_score']}/10
   • Verdict: {verdict['verdict']}
   • Recommendation: {verdict['recommendation']}

🔍 KEY FINDINGS:
{verdict['rationale']}

📋 NEXT STEPS:
   1. Review flagged clauses using provided explanations
   2. Use suggested redlines for negotiation
   3. Address compliance violations
   4. Consult legal advisor for final review

═══════════════════════════════════════════════════════════════════════════════
"""
        
        return summary


def run_contract_analysis(contract_text: str) -> Dict[str, Any]:
    """
    Convenience function to run full contract analysis
    
    Args:
        contract_text: The contract text to analyze
    
    Returns:
        Complete analysis results
    """
    crew = ContractAnalysisCrew()
    return crew.analyze_contract(contract_text)
