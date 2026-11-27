from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser
from app.services.ai.language import detect_language
from app.services.ai.intent import classify_intent_and_extract
from app.services.ai.prompt_guard import PromptGuard
from app.services.ai.provider import LLMProvider, StubLLMProvider
from app.services.ai.retrieval import PolicyRetrievalService
from app.services.banking.service import BankingService
from app.services.tools.gateway import BankingToolGateway


class BankingAIAgent:
    """Bilingual (AR/EN/Mixed) Banking AI orchestrator using typed tools & approved policy RAG."""

    provider: LLMProvider = StubLLMProvider()

    @classmethod
    async def handle_message(
        cls,
        db: AsyncSession,
        user: AuthenticatedUser,
        message: str,
        *,
        staff_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        lang = detect_language(message)
        is_valid, err = PromptGuard.validate_user_input(message)
        if not is_valid:
            await BankingService.record_audit(
                db, user, "AI_CHAT_BLOCKED", "chat:guard", "DENIED", {"reason": err}
            )
            await db.commit()
            reply = (
                "تم رفض الطلب لاعتبارات أمنية أو لانتهاك سياسة الوصول."
                if lang == "ar"
                else (err or "Request blocked by security guardrails.")
            )
            return {
                "reply": reply,
                "language": lang,
                "intent": "blocked",
                "entities": {},
                "citations": [],
                "blocked": True,
                "tool_used": None,
            }

        classified = classify_intent_and_extract(message)
        intent = classified.intent
        citations: List[Dict[str, Any]] = []
        tool_used: Optional[str] = None

        if intent == "balance":
            tool_used = "get_balances"
            res = await BankingToolGateway.execute(
                tool_name=tool_used, db=db, user=user, params={"reason": staff_reason}
            )
            accts = res["accounts"]
            if not accts:
                reply = "لا توجد حسابات مرتبطة بملفك." if lang == "ar" else "No accounts found for your profile."
            else:
                summary = "; ".join(f"{a['account_number_masked']}: {a['balance_formatted']}" for a in accts)
                reply = (
                    f"أرصدة حساباتك الحالية: {summary}"
                    if lang == "ar"
                    else f"Your current account balances: {summary}"
                )

        elif intent == "transactions":
            tool_used = "get_recent_transactions"
            res = await BankingToolGateway.execute(
                tool_name=tool_used, db=db, user=user, params={"reason": staff_reason}
            )
            txs = res["transactions"]
            if not txs:
                reply = "لا توجد معاملات حديثة." if lang == "ar" else "No recent transactions found."
            else:
                lines = ", ".join(f"{t['description']} ({t['amount_formatted']})" for t in txs[:3])
                reply = (
                    f"آخر معاملاتك: {lines}"
                    if lang == "ar"
                    else f"Recent transactions: {lines}"
                )

        elif intent == "card_block":
            tool_used = "block_card"
            res = await BankingToolGateway.execute(tool_name=tool_used, db=db, user=user)
            if res.get("blocked"):
                reply = (
                    f"تم حظر بطاقتك المنتهية بـ {res['card_last4']} بنجاح."
                    if lang == "ar"
                    else f"Your card ending in {res['card_last4']} has been blocked."
                )
            else:
                reply = "لم يتم العثور على بطاقة نشطة." if lang == "ar" else "No card found to block."

        elif intent == "transfer":
            reply = (
                "لإتمام التحويل بأمان، يرجى تأكيد تفاصيل التحويل عبر شاشة التحويلات."
                if lang == "ar"
                else "To complete a transfer safely with idempotency protection, please submit it via the Transfers screen."
            )

        elif intent == "complaint":
            reply = (
                "تم تسجيل ملاحظتك وسيقوم فريق خدمة العملاء بمراجعتها."
                if lang == "ar"
                else "Your complaint has been noted and routed to branch service staff for review."
            )

        elif intent == "policy_question":
            tool_used = "search_approved_policies"
            res = await BankingToolGateway.execute(
                tool_name=tool_used, db=db, user=user, params={"query": message}
            )
            citations = res["citations"]
            if not citations:
                reply = PolicyRetrievalService.abstention_for_language(lang)
            else:
                top = citations[0]
                _ = await cls.provider.generate(
                    PromptGuard.build_role_separated_messages(
                        "Answer strictly from cited approved bank policy.",
                        message,
                        [c["snippet"] for c in citations],
                    )
                )
                cite_tag = f"[{top['title']} — p.{top['page_number']}]"
                reply = (
                    f"وفقاً للسياسة المعتمدة {cite_tag}: {top['snippet']}"
                    if lang == "ar"
                    else f"Per approved policy {cite_tag}: {top['snippet']}"
                )

        else:
            reply = PolicyRetrievalService.abstention_for_language(lang)

        sanitized_reply, _ = PromptGuard.filter_output(reply)
        await BankingService.record_audit(
            db, user, "AI_CHAT_RESPONSE", "chat:turn", "SUCCESS", {"intent": intent, "language": lang, "tool_used": tool_used}
        )
        await db.commit()

        return {
            "reply": sanitized_reply,
            "language": lang,
            "intent": intent,
            "entities": classified.entities,
            "citations": citations,
            "blocked": False,
            "tool_used": tool_used,
        }
