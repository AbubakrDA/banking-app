from typing import Protocol, Dict, Any, runtime_checkable


class IntegrationNotConfiguredError(Exception):
    """Raised when a stub or disabled integration provider is invoked."""


@runtime_checkable
class IntegrationProvider(Protocol):
    integration_type: str
    provider_name: str


@runtime_checkable
class MobileMoneyProvider(IntegrationProvider, Protocol):
    async def send_payout(self, *, tenant_id: str, phone_masked: str, amount_minor: int, currency: str) -> Dict[str, Any]:
        ...


@runtime_checkable
class AgentNetworkProvider(IntegrationProvider, Protocol):
    async def cash_in(self, *, tenant_id: str, agent_code: str, amount_minor: int, currency: str) -> Dict[str, Any]:
        ...


class StubMobileMoneyProvider:
    integration_type = "mobile_money"
    provider_name = "stub"

    async def send_payout(self, *, tenant_id: str, phone_masked: str, amount_minor: int, currency: str) -> Dict[str, Any]:
        return {
            "status": "not_configured",
            "provider": self.provider_name,
            "integration_type": self.integration_type,
            "message": "Mobile money provider is not configured. Supply bank credentials and regulator approval.",
        }


class StubAgentNetworkProvider:
    integration_type = "agent_network"
    provider_name = "stub"

    async def cash_in(self, *, tenant_id: str, agent_code: str, amount_minor: int, currency: str) -> Dict[str, Any]:
        return {
            "status": "not_configured",
            "provider": self.provider_name,
            "integration_type": self.integration_type,
            "message": "Agent network provider is not configured. Supply bank credentials and regulator approval.",
        }
