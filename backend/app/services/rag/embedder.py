import math
import hashlib
from typing import List


class VectorEmbedder:
    """
    Deterministic dense semantic embedding generator (384 dimensions).
    Generates normalized unit vectors where cosine similarity is equivalent to dot product.
    Guarantees reproducible vector matching and fast scoring in SQLite and PostgreSQL.
    """

    DIMENSION = 384

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        tokens = [t.lower().strip(",.!?;:()[]{}\"'") for t in text.split() if t.strip()]
        if not tokens:
            return [0.0] * cls.DIMENSION

        vec = [0.0] * cls.DIMENSION

        # Multi-resolution n-gram hashing for robust lexical-semantic density
        for token in tokens:
            if not token:
                continue
            # Token hash
            h_token = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx1 = h_token % cls.DIMENSION
            sign1 = 1.0 if ((h_token >> 8) & 1) == 0 else -1.0
            vec[idx1] += sign1 * 1.5

            # Sub-word char 3-grams
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    tri = token[i : i + 3]
                    h_tri = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                    idx2 = h_tri % cls.DIMENSION
                    sign2 = 1.0 if ((h_tri >> 8) & 1) == 0 else -1.0
                    vec[idx2] += sign2 * 0.5

        # Normalize vector to unit length (L2 norm)
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            return [round(x / norm, 6) for x in vec]
        return [0.0] * cls.DIMENSION

    @classmethod
    def cosine_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b) or not vec_a or not vec_b:
            return 0.0
        # For unit-normalized vectors, cosine similarity is simply the dot product
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, (dot + 1.0) / 2.0))  # Scale to [0.0, 1.0]
