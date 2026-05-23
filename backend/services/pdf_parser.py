import PyPDF2
from typing import List
from utils.text_cleaner import TextCleaner

class PDFParser:
    """Extract and chunk PDF documents"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.cleaner = TextCleaner()
    
    def extract_text(self) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks
