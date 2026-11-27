import re
from typing import Literal

_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def detect_language(text: str) -> Literal["ar", "en", "mixed"]:
    """Detects Arabic ('ar'), English ('en'), or mixed ('mixed') text."""
    if not text:
        return "en"
    has_ar = bool(_ARABIC_RE.search(text))
    has_en = bool(_LATIN_RE.search(text))
    if has_ar and has_en:
        return "mixed"
    if has_ar:
        return "ar"
    return "en"
