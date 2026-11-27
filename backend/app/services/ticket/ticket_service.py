import re
import secrets
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional


class TicketService:
    """
    Enterprise Ticket Lifecycle & SLA Engine:
    - 8-stage lifecycle validation: new -> categorized -> assigned -> in_progress -> waiting_customer -> escalated -> resolved -> closed
    - Priority-based SLA calculation
    - Automatic issue classification & sentiment severity
    - Secure feedback token generation
    """

    VALID_TRANSITIONS = {
        "new": ["categorized", "assigned", "in_progress", "escalated", "resolved", "closed"],
        "categorized": ["assigned", "in_progress", "escalated", "resolved", "closed"],
        "assigned": ["in_progress", "waiting_customer", "escalated", "resolved", "closed"],
        "in_progress": ["waiting_customer", "escalated", "resolved", "closed"],
        "waiting_customer": ["in_progress", "escalated", "resolved", "closed"],
        "escalated": ["in_progress", "assigned", "resolved", "closed"],
        "resolved": ["closed", "in_progress"],  # can be reopened if customer not satisfied
        "closed": ["new"],  # Reopen as new if customer requests
    }

    SLA_HOURS = {
        "urgent": 2,
        "high": 8,
        "medium": 24,
        "low": 72,
    }

    @classmethod
    def auto_classify(cls, subject: str, description: str) -> Tuple[str, str]:
        text = f"{subject} {description}".lower()

        # 1. Category Classification
        if any(w in text for w in ["invoice", "charge", "refund", "billing", "payment", "credit card", "price"]):
            category = "billing"
        elif any(w in text for w in ["shipping", "tracking", "delivery", "carrier", "transit", "lost package"]):
            category = "shipping_delay"
        elif any(w in text for w in ["broken", "defective", "damaged", "faulty", "quality", "malfunction"]):
            category = "product_defect"
        elif any(w in text for w in ["appointment", "booking", "schedule", "reschedule", "calendar", "doctor"]):
            category = "appointment"
        elif any(w in text for w in ["login", "password", "2fa", "profile", "account", "unauthorized"]):
            category = "account"
        else:
            category = "general"

        # 2. Priority Classification & Severity
        if any(w in text for w in ["furious", "unacceptable", "lawyer", "emergency", "system down", "critical", "urgent"]):
            priority = "urgent"
        elif any(w in text for w in ["delayed", "failed", "broken", "angry", "terrible", "cancel"]):
            priority = "high"
        elif any(w in text for w in ["question", "minor", "suggestion", "feedback"]):
            priority = "low"
        else:
            priority = "medium"

        return category, priority

    @classmethod
    def calculate_sla_due_date(cls, priority: str) -> datetime:
        hours = cls.SLA_HOURS.get(priority.lower(), 24)
        return datetime.now(timezone.utc) + timedelta(hours=hours)

    @classmethod
    def validate_transition(cls, current_status: str, target_status: str) -> bool:
        if current_status == target_status:
            return True
        allowed = cls.VALID_TRANSITIONS.get(current_status, [])
        return target_status in allowed

    @classmethod
    def generate_ticket_number(cls, seq_num: int) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m")
        return f"TCK-{date_str}-{seq_num:04d}"

    @classmethod
    def generate_feedback_token(cls) -> str:
        return secrets.token_urlsafe(32)
