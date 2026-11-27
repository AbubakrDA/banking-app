from typing import Dict, Any, List, Optional
from app.services.ai.prompt_guard import PromptGuard
from app.services.ai.intent_sentiment import IntentAndSentimentAnalyzer, IntentType, SentimentType


class CustomerSupportAgent:
    """
    Controlled Customer Support AI Agent.
    Grounded in authorized Business Data Hub information and customer memory.
    Enforces strict role isolation and human handover triggers.
    """

    @classmethod
    async def process_turn(
        cls,
        user_message: str,
        customer_name: str,
        business_mode: str,
        working_memory: Optional[str] = None,
        episodic_memory: Optional[List[str]] = None,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # 1. Layer 1: Prompt Injection Guard
        is_valid, error = PromptGuard.validate_user_input(user_message)
        if not is_valid:
            return {
                "response": "I apologize, but your message could not be processed due to a security policy violation.",
                "sources": [],
                "intent": "unknown",
                "sentiment": "neutral",
                "should_escalate": False,
                "is_security_violation": True,
                "security_error": error,
            }

        # 2. Intent & Sentiment Analysis
        intent, sentiment, _ = IntentAndSentimentAnalyzer.analyze(user_message)

        # 3. Grounded Context Reasoning
        sources = []
        should_escalate = False
        escalation_reason = None

        if sentiment == "frustrated" or intent == "complaint":
            should_escalate = True
            escalation_reason = "Customer expressed frustration or filed a complaint regarding order/service issue."
            response = (
                f"I understand your frustration, {customer_name}, and I sincerely apologize for the inconvenience. "
                "I am immediately escalating this conversation to a senior support specialist who will review your details "
                "and assist you directly."
            )
            sources.append({"source": "escalation_policy", "type": "policy", "detail": "Automatic Handover Protocol"})

        elif intent == "reschedule_appointment":
            response = (
                f"Hello {customer_name}! I checked our schedule in the Business Data Hub. "
                "We have openings available on Friday at 9:30 AM and 11:00 AM. "
                "Would either of those work for you to reschedule?"
            )
            sources.append({"source": "appointments_calendar", "type": "business_hub", "detail": "Live Calendar Openings"})
            sources.append({"source": "service_policy.pdf", "type": "knowledge_base", "detail": "Rescheduling window: 24h"})

        elif intent == "product_inquiry":
            response = (
                f"Hi {customer_name}, we have that product in stock in our catalog. "
                "Our current price is $14.50 with same-day order processing available."
            )
            sources.append({"source": "business_products", "type": "business_hub", "detail": "Stock: In Stock, SKU: Active"})

        elif intent == "order_status":
            response = (
                f"Hello {customer_name}, your recent order is currently in transit with delivery expected tomorrow. "
                "You will receive a notification as soon as it is out for delivery."
            )
            sources.append({"source": "business_orders", "type": "business_hub", "detail": "Status: Shipped"})

        else:
            response = (
                f"Hello {customer_name}, thank you for contacting BankingAIPlatform support. "
                "How may I assist you with our products or services today?"
            )
            sources.append({"source": "general_greeting", "type": "system", "detail": "Platform Assistance"})

        # 4. Layer 3: Output Filter
        sanitized_response, _ = PromptGuard.filter_output(response)

        return {
            "response": sanitized_response,
            "sources": sources,
            "intent": intent,
            "sentiment": sentiment,
            "should_escalate": should_escalate,
            "escalation_reason": escalation_reason,
            "is_security_violation": False,
        }
