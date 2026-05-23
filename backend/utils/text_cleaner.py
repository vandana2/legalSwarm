import re

class TextCleaner:
    """Clean and normalize text from PDFs"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove extra whitespace and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,;:\-()\']', '', text)
        return text.strip()
    
    @staticmethod
    def extract_clauses(text: str) -> list:
        """Extract individual clauses from contract"""
        # Split by common clause markers
        clauses = re.split(r'(?:Section|Article|Clause|\d+\.)', text)
        return [clause.strip() for clause in clauses if clause.strip()]
