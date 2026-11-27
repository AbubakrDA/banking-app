from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.core.auth import AuthenticatedUser
from app.services.banking.service import BankingService, ValidationRuleError
from app.services.integrations.protocol import (
    MobileMoneyProvider,
    AgentNetworkProvider,
    StubMobileMoneyProvider,
    StubAgentNetworkProvider,
)


class IntegrationRegistry:
    """Registry for bank-selectable integration providers (all disabled by default)."""

    MOBILE_MONEY_PROVIDERS: Dict[str, type] = {
        "stub": StubMobileMoneyProvider,
    }
    AGENT_NETWORK_PROVIDERS: Dict[str, type] = {
        "stub": StubAgentNetworkProvider,
    }

    @classmethod
    def validate_startup_config(cls, cfg: Settings = settings) -> None:
        if cfg.MOBILE_MONEY_PROVIDER and cfg.MOBILE_MONEY_PROVIDER not in cls.MOBILE_MONEY_PROVIDERS:
            raise ValueError(f"Unknown MOBILE_MONEY_PROVIDER: '{cfg.MOBILE_MONEY_PROVIDER}'")
        if cfg.AGENT_NETWORK_PROVIDER and cfg.AGENT_NETWORK_PROVIDER not in cls.AGENT_NETWORK_PROVIDERS:
            raise ValueError(f"Unknown AGENT_NETWORK_PROVIDER: '{cfg.AGENT_NETWORK_PROVIDER}'")

    @classmethod
    def get_mobile_money_provider(cls, cfg: Settings = settings) -> Optional[MobileMoneyProvider]:
        if not cfg.ENABLE_MOBILE_MONEY_INTEGRATION or not cfg.MOBILE_MONEY_PROVIDER:
            return None
        cls.validate_startup_config(cfg)
        return cls.MOBILE_MONEY_PROVIDERS[cfg.MOBILE_MONEY_PROVIDER]()

    @classmethod
    def get_agent_network_provider(cls, cfg: Settings = settings) -> Optional[AgentNetworkProvider]:
        if not cfg.ENABLE_AGENT_NETWORK_INTEGRATION or not cfg.AGENT_NETWORK_PROVIDER:
            return None
        cls.validate_startup_config(cfg)
        return cls.AGENT_NETWORK_PROVIDERS[cfg.AGENT_NETWORK_PROVIDER]()

    @classmethod
    async def call_mobile_money_payout(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        *,
        phone_masked: str,
        amount_minor: int,
        currency: str,
        cfg: Settings = settings,
    ) -> Dict[str, Any]:
        provider = cls.get_mobile_money_provider(cfg)
        if provider is None:
            await BankingService.record_audit(
                db, user, "INTEGRATION_MOBILE_MONEY", "integration:mobile_money", "DENIED", {"reason": "disabled"}
            )
            await db.commit()
            raise ValidationRuleError("Mobile money integration is not enabled or configured.")
        result = await provider.send_payout(
            tenant_id=user.tenant_id,
            phone_masked=phone_masked,
            amount_minor=amount_minor,
            currency=currency,
        )
        await BankingService.record_audit(
            db,
            user,
            "INTEGRATION_MOBILE_MONEY",
            f"integration:mobile_money:{provider.provider_name}",
            "SUCCESS",
            {"amount_minor": amount_minor, "currency": currency, "result_status": result.get("status")},
        )
        await db.commit()
        return result

    @classmethod
    async def call_agent_network_cash_in(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        *,
        agent_code: str,
        amount_minor: int,
        currency: str,
        cfg: Settings = settings,
    ) -> Dict[str, Any]:
        provider = cls.get_agent_network_provider(cfg)
        if provider is None:
            await BankingService.record_audit(
                db, user, "INTEGRATION_AGENT_NETWORK", "integration:agent_network", "DENIED", {"reason": "disabled"}
            )
            await db.commit()
            raise ValidationRuleError("Agent network integration is not enabled or configured.")
        result = await provider.cash_in(
            tenant_id=user.tenant_id,
            agent_code=agent_code,
            amount_minor=amount_minor,
            currency=currency,
        )
        await BankingService.record_audit(
            db,
            user,
            "INTEGRATION_AGENT_NETWORK",
            f"integration:agent_network:{provider.provider_name}",
            "SUCCESS",
            {"amount_minor": amount_minor, "currency": currency, "result_status": result.get("status")},
        )
        await db.commit()
        return result
