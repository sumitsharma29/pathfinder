import math
import hashlib
from typing import List

from backend.app.ai.embeddings.base import EmbeddingProvider
from backend.app.core.config import settings


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic Mock Embedding Provider for offline testing and development.

    Produces unit-normalized dense vectors of dimension `settings.EMBEDDING_DIMENSION`
    derived deterministically from token hashes.
    """

    def __init__(self, dimension: int = settings.EMBEDDING_DIMENSION):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_query(self, text: str) -> List[float]:
        return self._generate_embedding(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_embedding(t) for t in texts]

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic unit-normalized pseudo-vector of configured dimension."""
        clean = (text or "").lower().strip()
        vec = [0.0] * self._dimension

        if not clean:
            # Return zero unit vector on first index
            vec[0] = 1.0
            return vec

        # Seed key concepts into specific vector segments for semantic overlap
        keywords = clean.split()
        for i, word in enumerate(keywords):
            # Compute hash integer
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % self._dimension
            weight = 1.0 / math.sqrt(i + 1)
            vec[idx] += weight

            # Also spread energy to neighboring dimensions
            vec[(idx + 1) % self._dimension] += weight * 0.5
            vec[(idx - 1) % self._dimension] += weight * 0.5

        # Compute Euclidean norm and normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0

        return vec
