import re
from typing import List, Dict, Any
from app.services.rag.embedder import VectorEmbedder


class HybridRetriever:
    """
    Enterprise RAG Hybrid Retrieval Engine:
    Combines dense semantic vector similarity with lexical keyword token matching.
    Applies reciprocal rank fusion, RAG poisoning filters, and source citation builders.
    """

    @classmethod
    def calculate_keyword_score(cls, query: str, content: str) -> float:
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return 0.0
        content_words = set(re.findall(r"\w+", content.lower()))
        matched = query_words.intersection(content_words)
        return len(matched) / len(query_words)

    @classmethod
    def search_and_rank(
        cls,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 5,
        alpha: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Ranks candidate chunks using hybrid score:
        score = alpha * vector_score + (1 - alpha) * keyword_score
        """
        query_vec = VectorEmbedder.embed_text(query)
        scored_candidates = []

        for item in chunks:
            content = item["content"]
            chunk_vec = item.get("embedding") or []

            # 1. Vector similarity
            vec_sim = VectorEmbedder.cosine_similarity(query_vec, chunk_vec) if chunk_vec else 0.0

            # 2. Lexical keyword score
            kw_sim = cls.calculate_keyword_score(query, content)

            # 3. Hybrid fusion
            hybrid_score = (alpha * vec_sim) + ((1.0 - alpha) * kw_sim)

            # 4. RAG Poisoning Check
            meta = item.get("chunk_metadata") or {}
            if meta.get("is_poisoned"):
                # Penalize or flag poisoned knowledge
                hybrid_score *= 0.1

            # 5. Extract structured citation
            doc_id = item.get("document_id", "unknown_doc")
            doc_title = item.get("document_title", "General Knowledge")
            col_name = item.get("collection_name", "Default")
            chunk_idx = item.get("chunk_index", 0)

            snippet = content[:150] + "..." if len(content) > 150 else content
            citation = {
                "source": doc_title,
                "document_id": doc_id,
                "collection": col_name,
                "chunk_index": chunk_idx,
                "snippet": snippet,
                "relevance_score": round(hybrid_score, 4),
            }

            scored_candidates.append({
                "chunk_id": item["id"],
                "document_id": doc_id,
                "document_title": doc_title,
                "collection_name": col_name,
                "content": content,
                "score": round(hybrid_score, 4),
                "sources": citation,
            })

        # Sort descending by hybrid score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:top_k]
