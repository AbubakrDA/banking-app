# Bank-Selectable Integrations

Integrations sit behind typed interfaces (`IntegrationProvider`, `MobileMoneyProvider`, `AgentNetworkProvider`) in `backend/app/services/integrations/`. All providers are **disabled by default** (`ENABLE_MOBILE_MONEY_INTEGRATION=False`, `ENABLE_AGENT_NETWORK_INTEGRATION=False`), and unknown provider names are rejected at startup.

## Prerequisites to Enable a Provider

Before enabling any `MobileMoneyProvider` or `AgentNetworkProvider` in staging or production, the bank must supply:
1. **API Credentials & Certificates:** Scoped mTLS certificates / API secrets stored in environment/secret manager (never in source code).
2. **Signed Commercial Contract & SLA:** Executed agreement with the telecom/mobile-money operator or agent network.
3. **Regulator Approval:** Written authorization from the relevant central bank / payment-system regulator.
4. **Sanctions & AML Review:** Compliance sign-off covering counterparty screening, transaction limits, and settlement reconciliation.
5. **Configuration & Feature Flag:** Explicit provider name in `MOBILE_MONEY_PROVIDER` / `AGENT_NETWORK_PROVIDER` and `ENABLE_*_INTEGRATION=True`.
