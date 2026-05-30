import re
from typing import List, Optional

import PyPDF2

from utils.text_cleaner import TextCleaner


class PDFParser:
    """Extract and pre-process text from PDF contract files."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.cleaner = TextCleaner()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text(self) -> str:
        """
        Extract all text from the PDF.

        - Handles pages that return None from extract_text().
        - Preserves section numbering and paragraph breaks.
        - Raises ValueError for image-only or empty PDFs so callers can
          return a clean 400 error.
        """
        pages: List[str] = []

        try:
            with open(self.file_path, "rb") as fh:
                reader = PyPDF2.PdfReader(fh)

                if len(reader.pages) == 0:
                    raise ValueError("PDF contains no pages.")

                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text: Optional[str] = page.extract_text()
                    except Exception as exc:
                        print(f"[PDFParser] Could not read page {page_num}: {exc}")
                        page_text = None

                    if page_text:
                        pages.append(page_text)

        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to open PDF: {exc}") from exc

        if not pages:
            raise ValueError(
                "No text could be extracted. The PDF may be image-only or corrupted. "
                "Please use a text-based PDF."
            )

        raw = "\n\n".join(pages)
        return self.cleaner.clean_contract_text(raw)

    def chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 100
    ) -> List[str]:
        """Split text into overlapping chunks for downstream processing."""
        if not text:
            return []
        chunks: List[str] = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks
