"""Explainer Agent - Translates legal jargon to plain English"""

class ExplainerAgent:
    def __init__(self):
        self.legal_terms = {
            "indemnification": "one party agrees to cover losses for the other",
            "force majeure": "unforeseeable circumstances that prevent contractual fulfillment",
            "termination for cause": "ending the contract due to a breach or violation",
            "non-compete clause": "agreement not to work for competitors"
        }
    
    def explain_clause(self, clause_text: str) -> str:
        """Explain legal clause in simple terms"""
        explanation = clause_text
        for term, definition in self.legal_terms.items():
            if term.lower() in clause_text.lower():
                explanation += f" | {term}: {definition}"
        return explanation
