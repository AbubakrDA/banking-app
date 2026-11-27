import re
from typing import List, Dict, Any, Tuple


class TextChunker:
    """
    Semantic text chunker with paragraph and sentence boundary preservation.
    Includes RAG poisoning detection to prevent hostile knowledge contamination.
    """

    POISON_PATTERNS = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"system\s*:\s*override",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"new\s+system\s+directive",
        r"disregard\s+all\s+security\s+rules",
    ]

    @classmethod
    def scan_for_rag_poisoning(cls, text: str) -> Tuple[bool, List[str]]:
        threats = []
        for pattern in cls.POISON_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(pattern)
        return len(threats) > 0, threats

    @classmethod
    def chunk_text(
        cls,
        text: str,
        chunk_size: int = 400,
        chunk_overlap: int = 50,
    ) -> List[Dict[str, Any]]:
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        # Split into semantic paragraphs first
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned_text) if p.strip()]

        raw_chunks: List[str] = []
        current_chunk: List[str] = []
        current_length = 0

        for p in paragraphs:
            # If paragraph itself is too large, split by sentences
            if len(p) > chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", p)
                for s in sentences:
                    s_len = len(s)
                    if current_length + s_len > chunk_size and current_chunk:
                        raw_chunks.append(" ".join(current_chunk))
                        # Keep overlap if possible
                        current_chunk = [s]
                        current_length = s_len
                    else:
                        current_chunk.append(s)
                        current_length += s_len + 1
            else:
                p_len = len(p)
                if current_length + p_len > chunk_size and current_chunk:
                    raw_chunks.append(" ".join(current_chunk))
                    current_chunk = [p]
                    current_length = p_len
                else:
                    current_chunk.append(p)
                    current_length += p_len + 1

        if current_chunk:
            raw_chunks.append(" ".join(current_chunk))

        # Format and scan chunks
        result: List[Dict[str, Any]] = []
        for idx, chunk_str in enumerate(raw_chunks):
            is_poisoned, threats = cls.scan_for_rag_poisoning(chunk_str)
            token_count = len(chunk_str.split())
            meta = {
                "chunk_index": idx,
                "character_length": len(chunk_str),
                "is_poisoned": is_poisoned,
            }
            if is_poisoned:
                meta["poison_threats"] = threats
                meta["security_flag"] = "RAG_POISONING_ATTEMPT_DETECTED"

            result.append({
                "chunk_index": idx,
                "content": chunk_str,
                "token_count": token_count,
                "metadata": meta,
            })

        return result
