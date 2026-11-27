import re
import uuid
from typing import Tuple, Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.nlp import QuestionCluster, LoggedQuestion
from app.services.rag.embedder import VectorEmbedder


class QuestionIntelligenceService:
    """
    NLP & Question Intelligence Engine:
    - Semantic question clustering using dense vector embeddings
    - Canonical question resolution
    - Language, intent, and sentiment detection
    - Knowledge gap discovery & draft FAQ generation
    - Trend analysis & frequency tracking
    """

    SIMILARITY_CLUSTER_THRESHOLD = 0.75

    @classmethod
    def detect_language(cls, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ["hola", "gracias", "por favor", "precio", "cuánto"]):
            return "es"
        elif any(w in lower for w in ["bonjour", "merci", "s'il vous plaît", "combien"]):
            return "fr"
        elif any(w in lower for w in ["hallo", "danke", "bitte", "wie viel"]):
            return "de"
        elif any(w in lower for w in ["مرحبا", "شكرا", "كم", "سعر"]):
            return "ar"
        return "en"

    @classmethod
    def classify_intent_and_category(cls, text: str) -> Tuple[str, str]:
        lower = text.lower()
        if any(w in lower for w in ["cost", "price", "pricing", "discount", "fee", "how much", "rate", "cuesta", "precio", "kostet", "preis", "coûte", "prix", "سعر", "تكلفة"]):
            return "pricing_inquiry", "sales"
        elif any(w in lower for w in ["shipping", "track", "delivery", "carrier", "when will", "arrived", "envío", "entrega", "lieferung", "livraison", "شحن", "توصيل"]):
            return "shipping_timeline", "logistics"
        elif any(w in lower for w in ["return", "refund", "exchange", "money back", "cancel", "reembolso", "devolución", "rückerstattung", "remboursement", "استرجاع", "استرداد"]):
            return "return_policy", "billing"
        elif any(w in lower for w in ["appointment", "booking", "schedule", "reschedule", "calendar", "slot", "cita", "termin", "rendez-vous", "موعد"]):
            return "appointment_booking", "service"
        elif any(w in lower for w in ["error", "bug", "crash", "password", "login", "broken", "fehler", "panne", "خطأ", "عطل"]):
            return "technical_support", "support"
        return "general_faq", "general"

    @classmethod
    def analyze_sentiment(cls, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ["furious", "angry", "terrible", "worst", "unacceptable", "scam"]):
            return "frustrated"
        elif any(w in lower for w in ["poor", "bad", "disappointed", "annoying", "delay"]):
            return "negative"
        elif any(w in lower for w in ["great", "thank", "love", "awesome", "perfect", "good", "helpful"]):
            return "positive"
        return "neutral"

    @classmethod
    async def cluster_and_log_question(
        cls,
        raw_text: str,
        tenant_id: str,
        customer_id: Optional[str],
        conversation_id: Optional[str],
        rag_confidence_score: float,
        db: AsyncSession,
    ) -> Tuple[LoggedQuestion, QuestionCluster]:
        q_vec = VectorEmbedder.embed_text(raw_text)
        lang = cls.detect_language(raw_text)
        intent, category = cls.classify_intent_and_category(raw_text)
        sentiment = cls.analyze_sentiment(raw_text)
        was_rag_matched = rag_confidence_score >= 0.65

        # 1. Search existing clusters for tenant
        res = await db.execute(select(QuestionCluster).where(QuestionCluster.tenant_id == tenant_id))
        existing_clusters = res.scalars().all()

        best_cluster: Optional[QuestionCluster] = None
        best_sim = 0.0

        for c in existing_clusters:
            if c.embedding:
                sim = VectorEmbedder.cosine_similarity(q_vec, c.embedding)
                if sim > best_sim:
                    best_sim = sim
                    best_cluster = c

        if best_cluster and best_sim >= cls.SIMILARITY_CLUSTER_THRESHOLD:
            # Match found: assign to existing cluster and update metrics
            best_cluster.frequency += 1
            if customer_id:
                # Approximate unique customer tracking
                best_cluster.unique_customer_count += 1

            if best_cluster.frequency >= 5:
                best_cluster.trend_direction = "surging"

            # Check for knowledge gap
            if not was_rag_matched and best_cluster.frequency >= 2:
                best_cluster.is_knowledge_gap = True
                if not best_cluster.suggested_faq_answer:
                    best_cluster.suggested_faq_answer = (
                        f"FAQ Draft for '{best_cluster.canonical_question}': "
                        "Automated draft synthesized from customer question volume. "
                        "Recommended response: Detail company policy and self-service steps here."
                    )
            target_cluster = best_cluster
        else:
            # Create a new semantic cluster
            cluster_id = str(uuid.uuid4())
            is_gap = not was_rag_matched
            suggested_faq = None
            if is_gap:
                suggested_faq = (
                    f"FAQ Draft for '{raw_text}': "
                    "New customer question without high-confidence RAG answer. "
                    "Recommended response: Document instructions in Knowledge Base."
                )

            target_cluster = QuestionCluster(
                id=cluster_id,
                tenant_id=tenant_id,
                canonical_question=raw_text,
                intent=intent,
                category=category,
                frequency=1,
                unique_customer_count=1,
                average_sentiment=sentiment,
                trend_direction="stable",
                is_knowledge_gap=is_gap,
                suggested_faq_answer=suggested_faq,
                embedding=q_vec,
            )
            db.add(target_cluster)
            await db.flush()

        # 2. Record LoggedQuestion
        logged_q = LoggedQuestion(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            cluster_id=target_cluster.id,
            customer_id=customer_id,
            conversation_id=conversation_id,
            raw_text=raw_text,
            detected_language=lang,
            detected_intent=intent,
            sentiment=sentiment,
            was_rag_matched=was_rag_matched,
            rag_confidence_score=rag_confidence_score,
        )
        db.add(logged_q)
        await db.commit()
        await db.refresh(logged_q)
        await db.refresh(target_cluster)

        return logged_q, target_cluster

