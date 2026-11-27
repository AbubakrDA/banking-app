import re
from dataclasses import dataclass, field
from typing import Dict, Any, Literal

IntentType = Literal[
    "balance",
    "transactions",
    "transfer",
    "card_block",
    "policy_question",
    "complaint",
    "unknown",
]

_AMOUNT_RE = re.compile(r"(?:\$|USD|EUR|SDG)?\s*(\d+(?:\.\d{1,2})?)\s*(USD|EUR|SDG|دولار|يورو|جنيه)?", re.IGNORECASE)


@dataclass
class ClassifiedIntent:
    intent: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)


def classify_intent_and_extract(text: str) -> ClassifiedIntent:
    """Rule-based bilingual (AR/EN/mixed) intent classifier and entity extractor."""
    low = text.lower()
    entities: Dict[str, Any] = {}

    m = _AMOUNT_RE.search(text)
    if m and any(k in low for k in ("transfer", "send", "pay", "حول", "تحويل", "ادفع", "$", "usd", "eur", "sdg")):
        raw_val = float(m.group(1))
        entities["amount_minor"] = int(round(raw_val * 100))
        curr = (m.group(2) or "USD").upper()
        if curr == "دولار":
            curr = "USD"
        elif curr == "يورو":
            curr = "EUR"
        elif curr == "جنيه":
            curr = "SDG"
        entities["currency"] = curr

    if any(k in low for k in ("block card", "freeze card", "lost card", "stolen card", "أوقف البطاقة", "حظر البطاقة", "تجميد البطاقة", "بطاقة مفقودة")):
        entities["card_action"] = "blocked"
        return ClassifiedIntent("card_block", 0.92, entities)

    if any(k in low for k in ("policy", "fee", "fees", "limit", "limits", "rule", "rules", "interest", "سياسة", "رسوم", "حدود", "قواعد", "شروط")):
        return ClassifiedIntent("policy_question", 0.88, entities)

    if any(k in low for k in ("transfer", "send money", "wire", "حول", "تحويل", "أرسل مبلغ")):
        return ClassifiedIntent("transfer", 0.90, entities)

    if any(k in low for k in ("balance", "how much", "my account", "رصيد", "رصيدي", "كم في حسابي")):
        return ClassifiedIntent("balance", 0.92, entities)

    if any(k in low for k in ("transaction", "transactions", "history", "statement", "recent", "معاملات", "عمليات", "كشف حساب", "آخر العمليات")):
        return ClassifiedIntent("transactions", 0.90, entities)

    if any(k in low for k in ("complaint", "dispute", "fraud", "issue", "problem", "شكوى", "اعتراض", "احتيال", "مشكلة")):
        return ClassifiedIntent("complaint", 0.85, entities)

    return ClassifiedIntent("unknown", 0.40, entities)
