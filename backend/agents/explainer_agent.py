"""Explainer Agent - Convert legal jargon to simple English"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Explanation:
    """Represents a clause explanation"""
    clause_id: int
    clause_type: str
    original_text: str
    simple_explanation: str
    key_terms: Dict[str, str]


class ExplainerAgent:
    """
    Convert legal jargon into simple, understandable English
    
    Purpose: Make contracts accessible to non-lawyers
    """
    
    # Dictionary of legal terms and plain English explanations
    LEGAL_GLOSSARY = {
        'indemnification': 'one party agrees to pay for losses/damages caused by the other party',
        'indemnify': 'to compensate someone for losses or damages',
        'force majeure': 'unforeseeable events (like natural disasters) that prevent fulfilling the contract',
        'liability': 'responsibility for damages or losses',
        'liable': 'legally responsible for paying damages',
        'warranty': 'a promise that something will work as described',
        'breach': 'breaking or failing to follow the terms of the contract',
        'termination': 'ending the contract',
        'terminate': 'to end something',
        'confidential': 'secret information that should not be shared',
        'non-disclosure': 'agreement not to reveal secret information',
        'assignment': 'transferring rights or responsibilities to another party',
        'assign': 'to transfer or give to another person/company',
        'intellectual property': 'creations of the mind like inventions, designs, names (copyright, patent, trademark)',
        'copyright': 'legal right to own and control creative works (writing, music, art)',
        'patent': 'exclusive right to make or sell an invention',
        'trademark': 'symbol or name identifying a company or product',
        'limitation of liability': 'a cap or limit on how much money someone must pay for damages',
        'disclaimer': 'statement saying something is NOT guaranteed',
        'auto-renewal': 'contract renews automatically unless you cancel',
        'perpetual': 'lasting forever',
        'severability': 'if one part of the contract is invalid, other parts still apply',
        'jurisdiction': 'which court system has authority to handle disputes',
        'governing law': 'which state/country laws apply to the contract',
        'arbitration': 'resolving disputes outside of court with a neutral third party',
        'venue': 'the location where legal disputes will be handled',
        'consideration': 'something of value exchanged between parties (payment, service, etc)',
        'mutual': 'something agreed to by both parties',
        'waiver': 'giving up a right or claim',
        'amendment': 'official change to the contract',
        'compliance': 'following rules, regulations, and laws',
        'represent': 'to guarantee something is true',
        'representation': 'a statement claiming something is true',
        'covenant': 'a serious promise or commitment',
        'successor': 'a person or company that takes over responsibilities',
        'survival': 'part of contract continues even after it ends',
        'effective date': 'when the contract officially starts',
        'term': 'the length of time the contract lasts',
        'renewal': 'extending the contract for another period',
        'default': 'failure to pay or follow contract terms',
    }
    
    # Common clause type explanations
    CLAUSE_TYPE_EXPLANATIONS = {
        'liability': 'This section defines who pays for damages and how much they\'re responsible for',
        'termination': 'This explains how and when either party can end the contract',
        'confidentiality': 'This section protects secret information and how it should be kept private',
        'ip': 'This defines who owns creative work and inventions created during the contract',
        'payment': 'This outlines payment amounts, due dates, and penalties for late payment',
        'warranty': 'This is a promise about the quality or performance of the service/product',
        'compliance': 'This ensures the contract follows all relevant laws and regulations',
        'renewal': 'This explains how the contract continues after the initial period ends',
        'assignment': 'This controls whether either party can transfer their rights to someone else',
        'amendment': 'This describes how the contract can be officially modified or changed',
        'force_majeure': 'This explains what happens if unforeseeable events prevent performance',
        'governing': 'This determines which court system and laws govern the contract',
        'general': 'General contract provision'
    }
    
    def __init__(self):
        self.explanations: List[Explanation] = []
    
    def explain_clause(self, clause: Dict[str, Any]) -> Explanation:
        """
        Explain a single clause in simple terms
        
        Args:
            clause: Dictionary with clause_id, clause_type, title, text
        
        Returns:
            Explanation object with simple explanation
        """
        clause_id = clause.get('clause_id', 0)
        clause_type = clause.get('clause_type', 'general')
        text = clause.get('text', '')
        
        # Get type explanation
        type_explanation = self.CLAUSE_TYPE_EXPLANATIONS.get(
            clause_type,
            f'This clause is about {clause_type}'
        )
        
        # Extract and explain legal terms
        key_terms = self._extract_and_explain_terms(text)
        
        # Generate simple explanation
        simple_explanation = self._generate_simple_explanation(
            clause_type, text, type_explanation, key_terms
        )
        
        explanation = Explanation(
            clause_id=clause_id,
            clause_type=clause_type,
            original_text=text[:200] + '...' if len(text) > 200 else text,
            simple_explanation=simple_explanation,
            key_terms=key_terms
        )
        
        self.explanations.append(explanation)
        return explanation
    
    def explain_clauses_batch(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Explain multiple clauses
        
        Args:
            clauses: List of clause dictionaries
        
        Returns:
            List of explanations as dictionaries
        """
        self.explanations = []
        results = []
        
        for clause in clauses:
            explanation = self.explain_clause(clause)
            results.append(asdict(explanation))
        
        return results
    
    def _extract_and_explain_terms(self, text: str) -> Dict[str, str]:
        """Extract legal terms and provide explanations"""
        found_terms = {}
        text_lower = text.lower()
        
        for term, explanation in self.LEGAL_GLOSSARY.items():
            if term in text_lower:
                found_terms[term] = explanation
        
        return found_terms
    
    def _generate_simple_explanation(self, clause_type: str, text: str, 
                                    type_explanation: str, key_terms: Dict[str, str]) -> str:
        """Generate a simple explanation combining clause type and key terms"""
        
        explanation = f"{type_explanation}\n\n"
        
        # Add key terms explanation
        if key_terms:
            explanation += "Key Terms in This Clause:\n"
            for term, definition in list(key_terms.items())[:5]:  # Show first 5 terms
                explanation += f"• {term.capitalize()}: {definition}\n"
        
        # Add plain language summary based on clause type
        if clause_type == 'liability':
            explanation += "\n📌 In Plain English:\nThis section explains who pays if something goes wrong and how much they have to pay."
        elif clause_type == 'termination':
            explanation += "\n📌 In Plain English:\nThis explains the process and timeline for ending this contract."
        elif clause_type == 'confidentiality':
            explanation += "\n📌 In Plain English:\nThis protects sensitive business information and requires keeping it secret."
        elif clause_type == 'ip':
            explanation += "\n📌 In Plain English:\nThis determines who owns the work created under this contract."
        elif clause_type == 'payment':
            explanation += "\n📌 In Plain English:\nThis outlines how much you pay, when you pay it, and what happens if you're late."
        elif clause_type == 'warranty':
            explanation += "\n📌 In Plain English:\nThis is a promise about how well the service/product will work."
        elif clause_type == 'compliance':
            explanation += "\n📌 In Plain English:\nThis ensures both parties follow all required laws and regulations."
        elif clause_type == 'renewal':
            explanation += "\n📌 In Plain English:\nThis explains what happens when the initial contract period ends."
        
        return explanation
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all explanations"""
        return {
            'total_clauses_explained': len(self.explanations),
            'explanations': [asdict(e) for e in self.explanations]
        }
