"""Risk Detector Agent - Identify legal and financial risks in clauses"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re


class RiskLevel(str, Enum):
    """Risk severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


@dataclass
class RiskDetection:
    """Represents a detected risk"""
    clause_id: int
    clause_type: str
    risk_level: RiskLevel
    reason: str
    keywords_found: List[str]
    recommendation: str


class RiskDetectorAgent:
    """
    Detect legal and financial risks in contract clauses
    
    Evaluates:
    - Unlimited liability
    - Auto-renewal traps
    - IP assignment risks
    - Unfair termination clauses
    - Payment risks
    - Compliance issues
    """
    
    # Risk patterns for different clause types
    RISK_PATTERNS = {
        'liability': {
            'critical': [
                r'unlimited\s+liability',
                r'liable\s+for\s+all\s+damages',
                r'no\s+limit(?:ation)?\s+(?:to\s+)?liability',
                r'indemnif[y|ied]\s+(?:.*?)\s+damages',
            ],
            'high': [
                r'liable\s+for.*?damages',
                r'indemnif[y|ied]',
                r'hold\s+harmless',
                r'liability\s+cap.*?(?:low|small|minimal)',
            ],
            'medium': [
                r'liability',
                r'damages',
                r'liable',
            ]
        },
        'termination': {
            'critical': [
                r'termination\s+without\s+cause',
                r'immediate\s+termination',
                r'terminate\s+at\s+will(?!\s+with\s+notice)',
            ],
            'high': [
                r'termination\s+for\s+convenience',
                r'terminate(?!d)?(?:\s+the)?.*?without.*?notice',
                r'no\s+notice\s+period',
                r'(?:can|may)\s+terminate.*?immediately',
            ],
            'medium': [
                r'termination',
                r'expire',
                r'end\s+date',
            ]
        },
        'ip': {
            'critical': [
                r'assign\s+(?:all\s+)?intellectual\s+property',
                r'all\s+work.*?(?:is|are)\s+(?:owned|assigned)',
                r'ip\s+assignment.*?unrestricted',
                r'transfer.*?all\s+rights',
            ],
            'high': [
                r'assign.*?intellectual\s+property',
                r'ip\s+ownership',
                r'copyright.*?assigned',
                r'patent.*?assignment',
            ],
            'medium': [
                r'intellectual\s+property',
                r'copyright',
                r'patent',
                r'trademark',
            ]
        },
        'renewal': {
            'critical': [
                r'auto.?renew',
                r'automatic\s+renewal',
                r'renew\s+automatically',
                r'unless.*?cancel.*?(?:in\s+writing|written)',
            ],
            'high': [
                r'renewal\s+(?:is\s+)?automatic',
                r'continue.*?automatically',
                r'(?:is\s+)?renewed.*?automatic(?:ally)?',
            ],
            'medium': [
                r'renewal',
                r'renew',
            ]
        },
        'payment': {
            'critical': [
                r'payment.*?non.?refundable',
                r'no\s+refund',
                r'all\s+fees.*?non.?refundable',
            ],
            'high': [
                r'late\s+payment.*?interest.*?(?:\d+%)',
                r'payment\s+penalty',
                r'late\s+fee',
            ],
            'medium': [
                r'payment\s+penalt',
                r'fees.*?non.?refundable',
            ]
        },
        'confidentiality': {
            'critical': [
                r'perpetual.*?confidential',
                r'confidential.*?forever',
                r'lifelong\s+confidentiality',
            ],
            'high': [
                r'broad\s+confidentiality',
                r'confidentiality.*?survival',
            ],
            'medium': [
                r'confidential',
                r'non.?disclosure',
            ]
        },
        'warranty': {
            'critical': [
                r'no\s+warranty',
                r'as\s+is.*?no\s+warrant',
                r'disclaimer.*?all\s+warrant',
            ],
            'high': [
                r'limited\s+warranty',
                r'warranty.*?disclaim',
            ],
            'medium': [
                r'warranty',
                r'warrant',
            ]
        },
        'compliance': {
            'critical': [
                r'no\s+compliance',
                r'exempt.*?compliance',
                r'not\s+subject\s+to.*?law',
            ],
            'high': [
                r'minimal\s+compliance',
                r'compliance\s+not\s+required',
            ],
            'medium': [
                r'compliance',
                r'regulatory',
            ]
        }
    }
    
    # Risk reasons explanations
    RISK_EXPLANATIONS = {
        'unlimited_liability': 'Your company could be liable for unlimited damages',
        'auto_renewal': 'Contract renews automatically - easy to forget and be locked in',
        'ip_assignment': 'You lose ownership of work created - company owns everything',
        'unfair_termination': 'Company can end contract immediately without notice',
        'non_refundable': 'All payments are non-refundable even if service fails',
        'broad_confidentiality': 'Information must stay confidential forever',
        'no_warranty': 'No guarantees about product/service quality',
        'compliance_gap': 'Clause may violate Indian laws or GDPR',
    }
    
    def __init__(self):
        self.detections: List[RiskDetection] = []
    
    def detect_risks(self, clause: Dict[str, Any]) -> RiskDetection:
        """
        Analyze a single clause for risks
        
        Args:
            clause: Dictionary with clause_id, clause_type, text
        
        Returns:
            RiskDetection object with risk assessment
        """
        clause_id = clause.get('clause_id', 0)
        clause_type = clause.get('clause_type', 'general')
        text = clause.get('text', '').lower()
        
        # Get risk patterns for this clause type
        patterns = self.RISK_PATTERNS.get(clause_type, {})
        
        risk_level = RiskLevel.MINIMAL
        keywords_found = []
        matched_reason = None
        
        # Check patterns in order of severity
        for severity in ['critical', 'high', 'medium']:
            if risk_level != RiskLevel.MINIMAL:
                break
                
            severity_patterns = patterns.get(severity, [])
            for pattern in severity_patterns:
                if re.search(pattern, text):
                    keywords_found.append(pattern)
                    risk_level = RiskLevel(severity.upper())
                    matched_reason = pattern
                    break
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_level, clause_type, text)
        
        detection = RiskDetection(
            clause_id=clause_id,
            clause_type=clause_type,
            risk_level=risk_level,
            reason=self._get_reason(clause_type, matched_reason),
            keywords_found=keywords_found,
            recommendation=recommendation
        )
        
        self.detections.append(detection)
        return asdict(detection)
    
    def detect_risks_batch(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple clauses in parallel (conceptually)
        
        Args:
            clauses: List of clause dictionaries
        
        Returns:
            List of risk detections as dictionaries
        """
        self.detections = []
        results = []
        
        for clause in clauses:
            detection = self.detect_risks(clause)
            results.append(detection)
        
        return results
    
    def _get_reason(self, clause_type: str, pattern: str) -> str:
        """Generate human-readable reason for detected risk"""
        if not pattern:
            return f"Risk detected in {clause_type} clause"
        
        # Map patterns to explanations
        if 'unlimited' in pattern or 'liable' in pattern:
            return self.RISK_EXPLANATIONS.get('unlimited_liability', 'Unlimited liability exposure')
        elif 'auto' in pattern or 'renewal' in pattern:
            return self.RISK_EXPLANATIONS.get('auto_renewal', 'Auto-renewal trap detected')
        elif 'assign' in pattern or 'ip' in pattern:
            return self.RISK_EXPLANATIONS.get('ip_assignment', 'IP ownership at risk')
        elif 'termination' in pattern or 'without' in pattern:
            return self.RISK_EXPLANATIONS.get('unfair_termination', 'Unfair termination clause')
        elif 'non.?refundable' in pattern:
            return self.RISK_EXPLANATIONS.get('non_refundable', 'Non-refundable payment risk')
        elif 'confidential' in pattern:
            return self.RISK_EXPLANATIONS.get('broad_confidentiality', 'Broad confidentiality obligations')
        elif 'warranty' in pattern or 'as is' in pattern:
            return self.RISK_EXPLANATIONS.get('no_warranty', 'No warranty provided')
        
        return f"Risk detected in {clause_type} clause"
    
    def _generate_recommendation(self, risk_level: RiskLevel, clause_type: str, text: str) -> str:
        """Generate recommendation to mitigate risk"""
        recommendations = {
            'liability': {
                'CRITICAL': 'Negotiate liability cap (e.g., fees paid in last 3-6 months)',
                'HIGH': 'Add reasonable liability limits',
                'MEDIUM': 'Review liability clause carefully',
            },
            'termination': {
                'CRITICAL': 'Require 30-60 day notice period before termination',
                'HIGH': 'Add notice period for termination',
                'MEDIUM': 'Clarify termination procedures',
            },
            'ip': {
                'CRITICAL': 'Negotiate IP ownership - retain rights to your work',
                'HIGH': 'Limit IP assignment to client-specific work only',
                'MEDIUM': 'Define IP ownership clearly',
            },
            'renewal': {
                'CRITICAL': 'Remove auto-renewal or add 60-day cancellation notice',
                'HIGH': 'Require explicit consent to renew',
                'MEDIUM': 'Add clear renewal terms',
            },
            'payment': {
                'CRITICAL': 'Negotiate refund clause for service failures',
                'HIGH': 'Add reasonable refund conditions',
                'MEDIUM': 'Clarify payment terms',
            },
            'confidentiality': {
                'CRITICAL': 'Limit confidentiality period (e.g., 3-5 years)',
                'HIGH': 'Add time limit on confidentiality obligations',
                'MEDIUM': 'Review confidentiality scope',
            },
            'warranty': {
                'CRITICAL': 'Negotiate reasonable warranties',
                'HIGH': 'Add limited warranties for services',
                'MEDIUM': 'Clarify warranty terms',
            },
            'compliance': {
                'CRITICAL': 'Ensure compliance with Indian IT Act 2000 and GDPR',
                'HIGH': 'Add compliance safeguards',
                'MEDIUM': 'Review compliance requirements',
            }
        }
        
        risk_str = risk_level.value
        return recommendations.get(clause_type, {}).get(risk_str, f'Review {clause_type} clause')
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all detected risks"""
        risk_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'MINIMAL': 0,
        }
        
        for detection in self.detections:
            risk_counts[detection.risk_level.value] += 1
        
        # Calculate overall risk score (0-10)
        total = len(self.detections)
        if total == 0:
            risk_score = 0.0
        else:
            risk_score = (
                (risk_counts['CRITICAL'] * 10 +
                 risk_counts['HIGH'] * 7 +
                 risk_counts['MEDIUM'] * 5 +
                 risk_counts['LOW'] * 2) / total
            )
        
        # Determine verdict
        if risk_score >= 8:
            verdict = "DO NOT SIGN"
        elif risk_score >= 6:
            verdict = "SIGN WITH MODIFICATIONS"
        else:
            verdict = "SAFE TO SIGN"
        
        return {
            'total_clauses_analyzed': total,
            'risk_distribution': risk_counts,
            'overall_risk_score': round(risk_score, 1),
            'verdict': verdict,
            'detections': [asdict(d) for d in self.detections]
        }
