import re
from typing import Dict, Tuple, List, Optional


class PromptGuard:
    """
    Bilingual (English & Arabic) Prompt Injection, Cross-Customer Refusal, & PII Output Guard.
    """

    INJECTION_PATTERNS = [
        # English injection & jailbreak patterns
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
        re.compile(r"disregard\s+(the\s+)?(system|initial)\s+(prompt|instructions)", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan|jailbroken)", re.IGNORECASE),
        re.compile(r"system\s+override\s*:", re.IGNORECASE),
        re.compile(r"output\s+(the\s+)?(system\s+prompt|secret\s+key|api\s+key)", re.IGNORECASE),
        re.compile(r"drop\s+(database|table)\b", re.IGNORECASE),
        re.compile(r"<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]", re.IGNORECASE),
        re.compile(r"</?system>|</?instruction>|---\s*END SYSTEM INSTRUCTIONS\s*---", re.IGNORECASE),
        re.compile(r"override\s+all\s+security\s+boundaries", re.IGNORECASE),
        # Arabic injection patterns
        re.compile(r"تجاهل\s+(كل\s+)?(التعليمات|الأوامر)\s*(السابقة)?"),
        re.compile(r"تجاوز\s+(جميع\s+)?(القواعد|الحماية|الحدود)"),
        re.compile(r"اعرض\s+(موجه\s+النظام|كلمة\s+المرور|المفتاح\s+السري)"),
        re.compile(r"أنت\s+الآن\s+في\s+وضع\s+المطور"),
    ]

    CROSS_CUSTOMER_PATTERNS = [
        re.compile(r"(other|another)\s+(customer|user|person)(?:'s)?\s+(account|balance|transactions|data)", re.IGNORECASE),
        re.compile(r"(عميل|مستخدم|شخص)\s+آخر", re.IGNORECASE),
        re.compile(r"(حساب|رصيد|بيانات)\s+(غيري|شخص\s+آخر)", re.IGNORECASE),
    ]

    # Raw 10-16 digit account/card numbers and national IDs must never appear in AI output
    _RAW_DIGITS_RE = re.compile(r"\b\d{10,16}\b")
    _NATIONAL_ID_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    MAX_MESSAGE_LENGTH = 4000

    @classmethod
    def validate_user_input(cls, text: str) -> Tuple[bool, Optional[str]]:
        if not text or not text.strip():
            return False, "Message content cannot be blank."
        if len(text) > cls.MAX_MESSAGE_LENGTH:
            return False, f"Message exceeds maximum allowed character length ({cls.MAX_MESSAGE_LENGTH})."
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(text):
                return False, "Security Violation: Prompt injection or instruction-override pattern detected."
        for pattern in cls.CROSS_CUSTOMER_PATTERNS:
            if pattern.search(text):
                return False, "Access denied: Requests for another customer's data are prohibited."
        return True, None

    @classmethod
    def sanitize_untrusted_envelope(cls, text: str) -> str:
        clean_text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        clean_text = re.sub(
            r"</?(customer_message_untrusted|system|instruction)\b[^>]*>",
            "[ESCAPED_TAG]",
            clean_text,
            flags=re.IGNORECASE,
        )
        return f"<customer_message_untrusted>\n{clean_text}\n</customer_message_untrusted>"

    @classmethod
    def build_role_separated_messages(
        cls,
        system_prompt: str,
        user_message: str,
        document_chunks: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if document_chunks:
            wrapped_docs = "\n".join(cls.sanitize_untrusted_envelope(c) for c in document_chunks)
            messages.append({"role": "user", "content": f"Untrusted Document Context:\n{wrapped_docs}"})
        messages.append({"role": "user", "content": cls.sanitize_untrusted_envelope(user_message)})
        return messages

    @classmethod
    def filter_output(cls, response_text: str) -> Tuple[str, bool]:
        flagged = False
        sanitized = response_text
        if cls._RAW_DIGITS_RE.search(sanitized):
            sanitized = cls._RAW_DIGITS_RE.sub("[REDACTED_ACCOUNT]", sanitized)
            flagged = True
        if cls._NATIONAL_ID_RE.search(sanitized):
            sanitized = cls._NATIONAL_ID_RE.sub("[REDACTED_ID]", sanitized)
            flagged = True
        for marker in ("SECRET_KEY", "END SYSTEM INSTRUCTIONS"):
            if marker in sanitized:
                sanitized = sanitized.replace(marker, "[REDACTED]")
                flagged = True
        return sanitized, flagged
