import re


class TextCleaner:
    """Clean and normalize text extracted from PDF contracts."""

    # Characters to preserve: word chars, whitespace, common punctuation
    _SAFE_CHARS = re.compile(r'[^\w\s\.,;:\-()\'"/%&@#\[\]{}]')

    # Soft hyphens / line-break hyphens: "termin-\nation" → "termination"
    _HYPHENATED_LINE_BREAK = re.compile(r'-\s*\n\s*')

    # Multiple consecutive blank lines → single blank line
    _MULTI_BLANK = re.compile(r'\n{3,}')

    # Mid-paragraph line wraps (line does NOT end with . ? ! :) → join
    _MID_PARA_WRAP = re.compile(r'(?<![.?!:])\n(?!\s*[\n\d])')

    # Excessive spaces (but NOT newlines)
    _MULTI_SPACE = re.compile(r'[^\S\n]{2,}')

    @classmethod
    def clean_contract_text(cls, text: str) -> str:
        """
        Full pipeline for raw PDF text:
        1. Fix soft hyphenation across line breaks.
        2. Join mid-paragraph line wraps.
        3. Collapse multiple blank lines.
        4. Remove non-printable / non-meaningful characters.
        5. Collapse repeated spaces.
        6. Strip leading/trailing whitespace.
        """
        if not text:
            return ""

        text = cls._HYPHENATED_LINE_BREAK.sub("", text)
        text = cls._MID_PARA_WRAP.sub(" ", text)
        text = cls._MULTI_BLANK.sub("\n\n", text)
        text = cls._SAFE_CHARS.sub("", text)
        text = cls._MULTI_SPACE.sub(" ", text)
        return text.strip()

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Lightweight cleaner (keeps original API for backwards compat).
        Collapses all whitespace to single spaces and strips non-safe chars.
        """
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = cls._SAFE_CHARS.sub("", text)
        return text.strip()

    @staticmethod
    def extract_clauses(text: str) -> list:
        """Split text on common clause markers (backwards-compat helper)."""
        clauses = re.split(r'(?:Section|Article|Clause|\d+\.)', text)
        return [c.strip() for c in clauses if c.strip()]
