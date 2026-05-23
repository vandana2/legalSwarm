"""Risk Detection Agent - Flags unfair and risky clauses"""

class RiskAgent:
    def __init__(self):
        self.risky_keywords = [
            "auto-renewal",
            "IP assignment",
            "liability cap",
            "indemnification",
            "termination without cause",
            "unlimited liability"
        ]
    
    def detect_risks(self, contract_text: str) -> list:
        """Identify risky clauses in contract"""
        risks = []
        for keyword in self.risky_keywords:
            if keyword.lower() in contract_text.lower():
                risks.append({
                    "keyword": keyword,
                    "risk_level": "high",
                    "description": f"Found potentially risky clause: {keyword}"
                })
        return risks
