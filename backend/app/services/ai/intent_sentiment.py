import re
from typing import Tuple, Literal

IntentType = Literal[
    "reschedule_appointment",
    "order_status",
    "product_inquiry",
    "complaint",
    "general_faq",
    "unknown",
]
SentimentType = Literal["positive", "neutral", "frustrated"]


class IntentAndSentimentAnalyzer:
    """
    Semantic Intent Detection & Sentiment Scorer.
    Identifies customer objective and tracks emotional escalation signals.
    """

    @classmethod
    def analyze(cls, text: str) -> Tuple[IntentType, SentimentType, float]:
        lower = text.lower()

        # 1. Intent Detection
        if any(w in lower for w in ["reschedule", "appointment", "booking", "dentist", "doctor", "slot", "calendar"]):
            intent: IntentType = "reschedule_appointment"
        elif any(w in lower for w in ["order", "shipping", "tracking", "delivery", "shipped", "package"]):
            intent = "order_status"
        elif any(w in lower for w in ["price", "cost", "stock", "product", "sku", "available", "buy"]):
            intent = "product_inquiry"
        elif any(w in lower for w in ["damaged", "broken", "angry", "terrible", "worst", "complaint", "refund", "scam"]):
            intent = "complaint"
        elif any(w in lower for w in ["hours", "policy", "refund policy", "return policy", "location"]):
            intent = "general_faq"
        else:
            intent = "unknown"

        # 2. Sentiment Analysis
        frustrated_signals = ["damaged", "broken", "unacceptable", "furious", "angry", "horrible", "refund", "waste", "scam"]
        positive_signals = ["thank", "thanks", "great", "excellent", "perfect", "appreciate", "helpful", "good"]

        frustrated_count = sum(1 for w in frustrated_signals if w in lower)
        positive_count = sum(1 for w in positive_signals if w in lower)

        if frustrated_count > 0:
            sentiment: SentimentType = "frustrated"
            confidence = min(0.95, 0.6 + (frustrated_count * 0.15))
        elif positive_count > 0:
            sentiment = "positive"
            confidence = min(0.95, 0.6 + (positive_count * 0.15))
        else:
            sentiment = "neutral"
            confidence = 0.85

        return intent, sentiment, confidence
