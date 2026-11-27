from typing import Protocol, List, Dict, Any, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Vendor-agnostic LLM provider interface (no vendor SDKs or API keys)."""

    provider_name: str

    async def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        ...


class StubLLMProvider:
    """Deterministic local stub provider for development and tests."""

    provider_name = "stub"

    async def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        return f"[StubLLM] Grounded response generated for verified banking request ({len(last_user)} chars)."
