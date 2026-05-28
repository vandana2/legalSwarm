"""Redline Agent - Suggest safer alternative clause language"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Redline:
    """Represents a suggested redline/modification"""
    clause_id: int
    clause_type: str
    risk_level: str
    original_clause: str
    suggested_clause: str
    reasoning: str
    key_changes: List[str]


class RedlineAgent:
    """
    Suggest safer, more balanced alternative language for risky clauses
    
    Purpose: Provide concrete negotiation language that protects both parties
    """
    
    # Redline suggestions for different risk types
    REDLINE_TEMPLATES = {
        'unlimited_liability': {
            'original_pattern': 'unlimited liability',
            'suggestion': 'Liability shall be limited to the total fees paid by Client in the 12 months preceding the claim.',
            'reasoning': 'Caps liability exposure and makes it proportional to contract value',
            'key_changes': [
                'Added specific liability cap (12 months of fees)',
                'Made liability proportional to contract value',
                'Protects both parties with defined limits'
            ]
        },
        'auto_renewal': {
            'original_pattern': 'auto-renewal|automatic renewal|renew automatically',
            'suggestion': 'This Agreement shall terminate on the expiration date unless either party provides written notice of intent to renew at least 60 days prior to expiration.',
            'reasoning': 'Requires active choice to renew instead of automatic continuation',
            'key_changes': [
                'Removed automatic renewal',
                'Requires written notice to renew',
                'Added 60-day notice period',
                'Prevents accidental lock-in'
            ]
        },
        'ip_assignment': {
            'original_pattern': 'assign.*?all.*?intellectual property|all work.*?owned',
            'suggestion': 'Client retains all intellectual property rights to its pre-existing materials. Provider retains all intellectual property rights to its general methodologies and tools. Work product specifically created for Client shall be jointly owned.',
            'reasoning': 'Allows both parties to retain value and use work in the future',
            'key_changes': [
                'Clarified pre-existing IP ownership',
                'Provider retains methodology rights',
                'Joint ownership of custom work',
                'Clearer boundaries for both parties'
            ]
        },
        'unfair_termination': {
            'original_pattern': 'terminate without cause|terminate immediately|terminate at will',
            'suggestion': 'Either party may terminate this Agreement with 30 days written notice. In case of material breach, termination is effective immediately upon written notice.',
            'reasoning': 'Provides stability while allowing exit for serious breaches',
            'key_changes': [
                'Added 30-day notice requirement',
                'Allows immediate termination only for material breach',
                'Provides transition period',
                'Protects both parties from sudden termination'
            ]
        },
        'non_refundable': {
            'original_pattern': 'non-refundable|no refund|all fees.*?non-refundable',
            'suggestion': 'Fees are non-refundable except in cases of material service failure. If Provider fails to deliver core services, Client is entitled to a pro-rata refund.',
            'reasoning': 'Protects vendor while ensuring client gets value',
            'key_changes': [
                'Added exception for material failure',
                'Defined pro-rata refund mechanism',
                'Balanced risk between parties',
                'Incentivizes service quality'
            ]
        },
        'broad_confidentiality': {
            'original_pattern': 'perpetual.*?confidential|confidential.*?forever|lifelong',
            'suggestion': 'Confidential Information shall remain confidential for a period of 3 years following termination of this Agreement, except for information that becomes publicly available through no fault of the receiving party.',
            'reasoning': 'Protects sensitive information while allowing eventual public use',
            'key_changes': [
                'Limited confidentiality to 3 years post-termination',
                'Added public domain exception',
                'Prevents indefinite restrictions',
                'Reasonable balance for business need'
            ]
        },
        'no_warranty': {
            'original_pattern': 'no warranty|as is.*?no warrant|disclaimer.*?all warrant',
            'suggestion': 'Provider warrants that services shall be performed in a professional manner consistent with industry standards. Provider disclaims warranties for third-party materials and client-provided content.',
            'reasoning': 'Provides basic assurance while limiting liability for external factors',
            'key_changes': [
                'Added professional standards warranty',
                'Carved out third-party materials',
                'Carve-out for client-provided content',
                'Reasonable quality baseline'
            ]
        },
        'payment_terms': {
            'original_pattern': 'late payment.*?interest|payment penalty',
            'suggestion': 'Invoices are due within 30 days. Late payments shall accrue interest at 1% per month (12% annually) or the maximum legal rate, whichever is less.',
            'reasoning': 'Incentivizes on-time payment with reasonable penalties',
            'key_changes': [
                'Specified payment due date',
                'Reasonable interest rate (1% monthly)',
                'Capped at legal maximum',
                'Clear penalty structure'
            ]
        },
        'compliance': {
            'original_pattern': 'no compliance|exempt.*?compliance|not subject to.*?law',
            'suggestion': 'Both parties shall comply with all applicable laws including the Indian IT Act 2000, GDPR (where applicable), and data protection regulations in their respective jurisdictions.',
            'reasoning': 'Ensures legal compliance and protects both parties',
            'key_changes': [
                'Added mandatory compliance requirement',
                'Referenced specific Indian laws',
                'Included GDPR compliance',
                'Protects from legal liability'
            ]
        }
    }
    
    def __init__(self):
        self.redlines: List[Redline] = []
    
    def suggest_redline(self, clause: Dict[str, Any], risk_level: str) -> Redline:
        """
        Suggest safer alternative language for a risky clause
        
        Args:
            clause: Dictionary with clause_id, clause_type, text
            risk_level: The detected risk level (CRITICAL, HIGH, MEDIUM)
        
        Returns:
            Redline object with suggested alternative
        """
        clause_id = clause.get('clause_id', 0)
        clause_type = clause.get('clause_type', 'general')
        text = clause.get('text', '')
        
        # Find matching redline template based on clause type and risk
        template = self._find_matching_template(clause_type, risk_level, text)
        
        if not template:
            template = self._generate_generic_redline(clause_type, text)
        
        redline = Redline(
            clause_id=clause_id,
            clause_type=clause_type,
            risk_level=risk_level,
            original_clause=text[:300] + '...' if len(text) > 300 else text,
            suggested_clause=template['suggestion'],
            reasoning=template['reasoning'],
            key_changes=template['key_changes']
        )
        
        self.redlines.append(redline)
        return redline
    
    def suggest_redlines_batch(self, clauses: List[Dict[str, Any]], 
                               risk_levels: List[str]) -> List[Dict[str, Any]]:
        """
        Suggest redlines for multiple clauses
        
        Args:
            clauses: List of clause dictionaries
            risk_levels: List of corresponding risk levels
        
        Returns:
            List of redline suggestions
        """
        self.redlines = []
        results = []
        
        for clause, risk_level in zip(clauses, risk_levels):
            redline = self.suggest_redline(clause, risk_level)
            results.append(asdict(redline))
        
        return results
    
    def _find_matching_template(self, clause_type: str, risk_level: str, text: str) -> Dict[str, Any]:
        """Find appropriate redline template based on clause type"""
        import re
        
        text_lower = text.lower()
        
        # Map clause types to redline keys
        type_mapping = {
            'liability': 'unlimited_liability',
            'termination': 'unfair_termination',
            'ip': 'ip_assignment',
            'renewal': 'auto_renewal',
            'payment': 'payment_terms',
            'confidentiality': 'broad_confidentiality',
            'warranty': 'no_warranty',
            'compliance': 'compliance'
        }
        
        redline_key = type_mapping.get(clause_type)
        if not redline_key:
            return None
        
        template = self.REDLINE_TEMPLATES.get(redline_key)
        if template:
            return template
        
        return None
    
    def _generate_generic_redline(self, clause_type: str, text: str) -> Dict[str, Any]:
        """Generate generic redline for unmatched clause types"""
        return {
            'suggestion': f'[Negotiate {clause_type} clause to be fair to both parties]',
            'reasoning': 'Review this clause to ensure it protects your interests while remaining reasonable',
            'key_changes': [
                'Consider adding protections for your side',
                'Ensure terms are reciprocal',
                'Define clear boundaries and limits'
            ]
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all suggested redlines"""
        total = len(self.redlines)
        critical_count = sum(1 for r in self.redlines if r.risk_level == 'CRITICAL')
        high_count = sum(1 for r in self.redlines if r.risk_level == 'HIGH')
        
        return {
            'total_redlines': total,
            'critical_suggestions': critical_count,
            'high_suggestions': high_count,
            'redlines': [asdict(r) for r in self.redlines],
            'summary': f'Suggested {total} modifications to safer language ({critical_count} critical, {high_count} high priority)'
        }
