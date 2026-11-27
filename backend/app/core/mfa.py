from typing import Protocol, Optional, runtime_checkable
from app.core.config import Settings, settings


@runtime_checkable
class MFAProvider(Protocol):
    """Pluggable MFA verification interface; bank selects concrete provider."""

    provider_name: str

    async def verify(self, *, user_id: str, action: str, code: Optional[str]) -> bool:
        ...


class StubMFAProvider:
    """Default stub MFA provider. Accepts any non-empty 6+ char code when enabled."""

    provider_name = "stub"

    async def verify(self, *, user_id: str, action: str, code: Optional[str]) -> bool:
        return bool(code and len(code.strip()) >= 6)


def get_mfa_provider(cfg: Settings = settings) -> MFAProvider:
    if cfg.MFA_PROVIDER == "stub":
        return StubMFAProvider()
    raise ValueError(f"Unknown MFA_PROVIDER: '{cfg.MFA_PROVIDER}'")
