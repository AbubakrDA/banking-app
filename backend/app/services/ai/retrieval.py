import re
from dataclasses import dataclass
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banking import PolicyDocument, PolicyChunk


@dataclass
class PolicyCitation:
    policy_id: str
    title: str
    page_number: int
    snippet: str


SAFE_ABSTENTION_EN = (
    "I cannot answer that policy question because no approved bank policy document provides relevant evidence. "
    "Please contact a branch officer or wait for compliance-approved documentation."
)
SAFE_ABSTENTION_AR = (
    "لا أستطيع الإجابة عن هذا السؤال لعدم توفر مستند سياسة بنكية معتمد يحتوي على معلومات ذات صلة. "
    "يرجى التواصل مع موظف الفرع أو مراجعة السياسات المعتمدة."
)

_TOKEN_RE = re.compile(r"[\w\u0600-\u06FF]{3,}", re.UNICODE)
_STOPWORDS = {"the", "and", "for", "with", "what", "are", "how", "can", "policy", "fee", "fees", "في", "من", "على", "عن", "هل", "سياسة", "رسوم"}


class PolicyRetrievalService:
    """Retrieves evidence strictly from PolicyDocument rows with status == 'approved'."""

    @classmethod
    async def search_approved(
        cls,
        db: AsyncSession,
        tenant_id: str,
        query: str,
        top_k: int = 3,
    ) -> List[PolicyCitation]:
        tokens = {t.lower() for t in _TOKEN_RE.findall(query) if t.lower() not in _STOPWORDS}
        if not tokens:
            return []

        stmt = (
            select(PolicyChunk, PolicyDocument)
            .join(PolicyDocument, PolicyChunk.policy_id == PolicyDocument.id)
            .where(
                PolicyDocument.tenant_id == tenant_id,
                PolicyDocument.status == "approved",
            )
        )
        rows = (await db.execute(stmt)).all()

        scored: List[tuple[int, PolicyChunk, PolicyDocument]] = []
        for chunk, doc in rows:
            haystack = f"{doc.title} {chunk.content}".lower()
            overlap = sum(1 for tok in tokens if tok in haystack)
            if overlap > 0:
                scored.append((overlap, chunk, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            PolicyCitation(
                policy_id=doc.id,
                title=doc.title,
                page_number=chunk.page_number,
                snippet=chunk.content[:280],
            )
            for _, chunk, doc in scored[:top_k]
        ]

    @staticmethod
    def abstention_for_language(language: str) -> str:
        return SAFE_ABSTENTION_AR if language == "ar" else SAFE_ABSTENTION_EN
