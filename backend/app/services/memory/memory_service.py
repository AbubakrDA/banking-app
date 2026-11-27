import re
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any, List
from app.models.memory import CustomerMemory


class MemoryService:
    """
    Enterprise Customer Memory Service:
    - 3-tier memory management: Working (session/context), Episodic (events), Semantic (preferences)
    - Anti-Poisoning Filter (Spec §7, GEMINI.md Rule 4)
    - Untrusted Data Envelope formatting for AI agent context
    - Expiration & TTL enforcement
    """

    MEMORY_POISON_PATTERNS = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"admin\s+permission|full\s+access|root\s+access",
        r"override\s+system|system\s*:\s*override",
        r"bypass\s+(?:all\s+)?rules|security|payment",
        r"disregard\s+billing|zero\s+price|100%\s+discount",
        r"you\s+are\s+now\s+(?:unrestricted|dan|jailbroken)",
    ]

    @classmethod
    def validate_memory_content(cls, key: str, value: str) -> Tuple[bool, Optional[str]]:
        combined = f"{key} {value}"
        for pattern in cls.MEMORY_POISON_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return False, f"Hostile memory injection detected: matching pattern '{pattern}'"
        return True, None

    @classmethod
    def format_context_envelope(
        cls,
        working_mem: Dict[str, str],
        episodic_mem: List[Dict[str, Any]],
        semantic_mem: Dict[str, str],
    ) -> str:
        """
        Formats active memories into an untrusted XML envelope per GEMINI.md.
        """
        envelope_lines = [
            '<customer_memory_untrusted provenance="verified_customer_store">',
            "  <working_context>",
        ]
        for k, v in working_mem.items():
            envelope_lines.append(f'    <item key="{k}">{v}</item>')
        envelope_lines.append("  </working_context>")

        envelope_lines.append("  <semantic_preferences>")
        for k, v in semantic_mem.items():
            envelope_lines.append(f'    <trait key="{k}">{v}</trait>')
        envelope_lines.append("  </semantic_preferences>")

        envelope_lines.append("  <episodic_history>")
        for ep in episodic_mem[:5]:  # Top 5 most recent episodic events
            key = ep.get("key", "event")
            val = ep.get("value", "")
            envelope_lines.append(f'    <event name="{key}">{val}</event>')
        envelope_lines.append("  </episodic_history>")
        envelope_lines.append("</customer_memory_untrusted>")

        return "\n".join(envelope_lines)
