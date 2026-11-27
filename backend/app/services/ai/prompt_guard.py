import re
from typing import Dict, Tuple, List, Optional


class PromptGuard:
    """
    5-Layer Defense-in-Depth Prompt Injection & Safety Guard.
    Enforces GEMINI.md and Specification §7 security boundaries.
    """

    # Layer 1: Known prompt injection / jailbreak patterns
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
        re.compile(r"disregard\s+(the\s+)?(system|initial)\s+(prompt|instructions)", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan|jailbroken)", re.IGNORECASE),
        re.compile(r"system\s+override\s*:", re.IGNORECASE),
        re.compile(r"output\s+(the\s+)?(system\s+prompt|secret\s+key|api\s+key)", re.IGNORECASE),
        re.compile(r"drop\s+(database|table)\b", re.IGNORECASE),
        re.compile(r"<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]", re.IGNORECASE),
        re.compile(r"</?system>|</?instruction>|---\s*END SYSTEM INSTRUCTIONS\s*---", re.IGNORECASE),
        re.compile(r"override\s+all\s+security\s+boundaries", re.IGNORECASE),
    ]

    MAX_MESSAGE_LENGTH = 4000

    @classmethod
    def validate_user_input(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Layer 1: Validates input length and checks for adversarial injection vectors.
        """
        if not text or not text.strip():
            return False, "Message content cannot be blank."

        if len(text) > cls.MAX_MESSAGE_LENGTH:
            return False, f"Message exceeds maximum allowed character length ({cls.MAX_MESSAGE_LENGTH})."

        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(text):
                return False, "Security Violation: Prompt injection or instruction-override pattern detected."

        return True, None

    @classmethod
    def sanitize_untrusted_envelope(cls, text: str) -> str:
        """
        Layer 2: Wraps user text in an untrusted data envelope, neutralizing prompt escape attempts.
        """
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
        """
        Layer 2: Builds role-separated LLM messages so untrusted user/document content
        is never concatenated into the privileged system message.
        """
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if document_chunks:
            wrapped_docs = "\n".join(cls.sanitize_untrusted_envelope(c) for c in document_chunks)
            messages.append({"role": "user", "content": f"Untrusted Document Context:\n{wrapped_docs}"})
        messages.append({"role": "user", "content": cls.sanitize_untrusted_envelope(user_message)})
        return messages

    @classmethod
    def filter_output(cls, response_text: str) -> Tuple[str, bool]:
        """
        Layer 3: Scans AI response for accidental system prompt or secret leakage.
        """
        flagged = False
        leak_patterns = [
            r"banking-ai-platform-dev-secret",
            r"SECRET_KEY",
            r"system instructions are:",
            r"you are an AI designed by",
        ]
        sanitized = response_text
        for p in leak_patterns:
            if re.search(p, sanitized, re.IGNORECASE):
                sanitized = re.sub(p, "[REDACTED_SYSTEM_CONTENT]", sanitized, flags=re.IGNORECASE)
                flagged = True

        return sanitized, flagged
