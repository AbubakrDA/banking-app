from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser
from app.services.banking.service import BankingService, AccessDeniedError
from app.services.ai.retrieval import PolicyRetrievalService


def _fmt_minor(amount_minor: int, currency: str) -> str:
    return f"{currency} {amount_minor / 100:,.2f}"


class BankingToolGateway:
    """
    Registered, typed tool gateway for AI components.
    Default-deny for unknown tools; every call routes through BankingService with RBAC, ownership, and audit logging.
    """

    REGISTERED_TOOLS = frozenset({
        "get_balances",
        "get_recent_transactions",
        "block_card",
        "search_approved_policies",
    })

    @classmethod
    async def execute(
        cls,
        *,
        tool_name: str,
        db: AsyncSession,
        user: AuthenticatedUser,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        params = params or {}
        if tool_name not in cls.REGISTERED_TOOLS:
            await BankingService.record_audit(
                db, user, "AI_TOOL_EXECUTION", f"tool:{tool_name}", "DENIED", {"reason": "unknown_tool"}
            )
            await db.commit()
            raise AccessDeniedError(f"Tool '{tool_name}' is not registered.")

        if tool_name == "get_balances":
            if user.role in ("hr", "marketing"):
                await BankingService.record_audit(
                    db, user, "AI_TOOL_EXECUTION", "tool:get_balances", "DENIED", {"reason": "department_restricted"}
                )
                await db.commit()
                raise AccessDeniedError("Department role cannot access account balances.")
            accounts = await BankingService.list_accounts(db, user, reason=params.get("reason"))
            return {
                "accounts": [
                    {
                        "id": a.id,
                        "account_number_masked": a.account_number_masked,
                        "account_type": a.account_type,
                        "currency": a.currency,
                        "balance_minor": a.balance_minor,
                        "balance_formatted": _fmt_minor(a.balance_minor, a.currency),
                    }
                    for a in accounts
                ]
            }

        if tool_name == "get_recent_transactions":
            if user.role in ("hr", "marketing"):
                await BankingService.record_audit(
                    db, user, "AI_TOOL_EXECUTION", "tool:get_recent_transactions", "DENIED", {"reason": "department_restricted"}
                )
                await db.commit()
                raise AccessDeniedError("Department role cannot access transaction history.")
            txs, total = await BankingService.list_transactions(
                db, user, page=1, page_size=5, reason=params.get("reason")
            )
            return {
                "total": total,
                "transactions": [
                    {
                        "id": t.id,
                        "tx_type": t.tx_type,
                        "amount_minor": t.amount_minor,
                        "amount_formatted": _fmt_minor(t.amount_minor, t.currency),
                        "description": t.description,
                    }
                    for t in txs
                ],
            }

        if tool_name == "block_card":
            if user.role != "customer":
                raise AccessDeniedError("Only customers can block their own cards via chat.")
            cards = await BankingService.list_cards(db, user)
            if not cards:
                return {"blocked": False, "reason": "no_cards_found"}
            target = cards[0]
            updated = await BankingService.update_card_status(db, user, target.id, "blocked")
            return {"blocked": True, "card_last4": updated.card_last4, "status": updated.status}

        if tool_name == "search_approved_policies":
            query = str(params.get("query", ""))
            citations = await PolicyRetrievalService.search_approved(db, user.tenant_id, query)
            await BankingService.record_audit(
                db, user, "AI_POLICY_RETRIEVAL", "policies:approved", "SUCCESS", {"citation_count": len(citations)}
            )
            await db.commit()
            return {
                "citations": [
                    {
                        "policy_id": c.policy_id,
                        "title": c.title,
                        "page_number": c.page_number,
                        "snippet": c.snippet,
                    }
                    for c in citations
                ]
            }

        raise AccessDeniedError("Unhandled tool")


ToolGatewayService = BankingToolGateway
