"""Parser Agent - Extract and structure contract clauses"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class Clause:
    """Represents a single clause in a contract"""
    clause_id: int
    clause_number: str  # e.g., "Section 1", "Article 2.3"
    clause_type: str    # e.g., "liability", "termination", "confidentiality"
    title: str          # Clause title
    text: str           # Full clause text
    section: str        # Parent section/article

class ParserAgent:
    """
    Extract and structure contract clauses from text
    
    Process:
    1. Split document into sections/articles
    2. Identify clause types
    3. Extract clause content
    4. Structure as JSON output
    """
    
    # Common clause type keywords
    CLAUSE_TYPES = {
        'liability': ['liability', 'liable', 'damages', 'indemnif'],
        'termination': ['termination', 'terminate', 'expiration', 'end date'],
        'confidentiality': ['confidential', 'non-disclosure', 'nda', 'secret'],
        'ip': ['intellectual property', 'ip', 'copyright', 'patent', 'trademark'],
        'payment': ['payment', 'fees', 'price', 'compensation', 'invoice'],
        'warranty': ['warranty', 'warrant', 'guarantee', 'represent'],
        'limitation': ['limitation', 'limit', 'cap', 'maximum', 'exclude'],
        'governing': ['governing law', 'jurisdiction', 'dispute', 'arbitration'],
        'renewal': ['renewal', 'auto-renew', 'automatic renewal', 'extend'],
        'assignment': ['assign', 'transfer', 'delegate', 'subcontract'],
        'amendment': ['amendment', 'modify', 'change', 'alter'],
        'force_majeure': ['force majeure', 'unforeseeable', 'act of god'],
        'compliance': ['comply', 'compliance', 'regulation', 'law', 'statute'],
        'general': ['general', 'miscellaneous', 'other']
    }
    
    # Section identifiers
    SECTION_PATTERNS = [
        r'^(Section|Article|Clause|Part)\s+(\d+(?:\.\d+)*)',  # Section 1, Article 2.3
        r'^(\d+(?:\.\d+)*)\s*\.',  # 1., 2.1.
        r'^(I+|i+|[IVX]+)\.',  # I., II., iii.
    ]
    
    def __init__(self):
        self.clauses: List[Clause] = []
        self.clause_counter = 1
        self.current_section = "General"
    
    def extract_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep structure
        text = re.sub(r'[^\w\s\.,;:\-()\'"\n]', '', text)
        return text.strip()
    
    def identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify and extract sections/articles"""
        sections = []
        current_section = None
        current_text = ""
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            is_section = False
            for pattern in self.SECTION_PATTERNS:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous section
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'text': current_text.strip()
                        })
                    current_section = line
                    current_text = ""
                    is_section = True
                    break
            
            if not is_section and current_section:
                current_text += " " + line
        
        # Add last section
        if current_section:
            sections.append({
                'title': current_section,
                'text': current_text.strip()
            })
        
        return sections
    
    def identify_clause_type(self, text: str) -> str:
        """Identify the type of clause based on keywords"""
        text_lower = text.lower()
        
        # Count keyword matches for each type
        type_scores = {}
        for clause_type, keywords in self.CLAUSE_TYPES.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[clause_type] = score
        
        # Return the type with highest score, default to 'general'
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return 'general'
    
    def extract_clause_title(self, section_title: str, text: str) -> str:
        """Extract or generate clause title"""
        # First try to get title from section header
        if section_title:
            # Remove numbering from section title
            title = re.sub(r'^(Section|Article|Clause|Part)\s+\d+(?:\.\d+)*\s*:?\s*', '', section_title, flags=re.IGNORECASE)
            if title:
                return title.strip()
        
        # Extract first sentence as title
        sentences = re.split(r'[.!?]', text)
        if sentences:
            return sentences[0][:100].strip()
        
        return "Unnamed Clause"
    
    def parse_document(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Main parsing function - converts PDF text to structured clauses
        
        Args:
            raw_text: Raw text extracted from PDF
        
        Returns:
            List of structured clause dictionaries
        """
        # Clean the text
        text = self.extract_text(raw_text)
        
        if not text:
            return []
        
        # Identify sections
        sections = self.identify_sections(text)
        
        if not sections:
            # If no clear sections, treat entire text as one section
            sections = [{'title': 'General', 'text': text}]
        
        self.clauses = []
        
        # Process each section
        for section_idx, section in enumerate(sections):
            section_title = section.get('title', '')
            section_text = section.get('text', '')
            
            # Update current section for tracking
            self.current_section = section_title
            
            # Split section into individual clauses (by sentences or paragraphs)
            clause_texts = self._split_into_clauses(section_text)
            
            # Create clause objects
            for clause_text in clause_texts:
                if len(clause_text.strip()) < 20:  # Skip very short clauses
                    continue
                
                clause_type = self.identify_clause_type(clause_text)
                title = self.extract_clause_title(section_title, clause_text)
                
                clause = Clause(
                    clause_id=self.clause_counter,
                    clause_number=section_title,
                    clause_type=clause_type,
                    title=title,
                    text=clause_text.strip(),
                    section=self.current_section
                )
                
                self.clauses.append(clause)
                self.clause_counter += 1
        
        return [asdict(clause) for clause in self.clauses]
    
    def _split_into_clauses(self, text: str) -> List[str]:
        """Split section text into individual clauses"""
        # Split by paragraph breaks first
        paragraphs = text.split('\n\n')
        
        clauses = []
        for paragraph in paragraphs:
            if paragraph.strip():
                # Further split by sentence-like patterns
                # But keep related sentences together
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                
                # Group 2-3 sentences together as one clause
                clause_text = ""
                for sentence in sentences:
                    clause_text += sentence + " "
                    # Start new clause after 2 sentences or certain length
                    if len(clause_text.split('.')) >= 2 or len(clause_text) > 500:
                        clauses.append(clause_text.strip())
                        clause_text = ""
                
                # Add remaining text
                if clause_text.strip():
                    clauses.append(clause_text.strip())
        
        return [c.strip() for c in clauses if c.strip()]
    
    def to_json(self) -> str:
        """Convert parsed clauses to JSON"""
        return json.dumps([asdict(clause) for clause in self.clauses], indent=2)
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert parsed clauses to list of dictionaries"""
        return [asdict(clause) for clause in self.clauses]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of parsed document"""
        type_counts = {}
        for clause in self.clauses:
            clause_type = clause.clause_type
            type_counts[clause_type] = type_counts.get(clause_type, 0) + 1
        
        return {
            'total_clauses': len(self.clauses),
            'clause_types': type_counts,
            'clauses': [asdict(clause) for clause in self.clauses]
        }
