from typing import Protocol, Dict, Any, runtime_checkable


@runtime_checkable
class SanctionsScreeningProvider(Protocol):
    """Pluggable sanctions-screening interface for S5 (Risk & Sanctions)."""

    provider_name: str

    async def screen_transfer(self, *, tenant_id: str, transfer_reference: str, is_cross_border: bool) -> Dict[str, Any]:
        ...


class StubSanctionsScreeningProvider:
    """Placeholder sanctions-screening stub; blocks cross-border until compliance clearance flag is set."""

    provider_name = "stub"

    async def screen_transfer(self, *, tenant_id: str, transfer_reference: str, is_cross_border: bool) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "cleared": not is_cross_border,
            "status": "blocked_pending_sanctions_decision" if is_cross_border else "domestic_not_applicable",
        }
