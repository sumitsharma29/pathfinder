from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract Base Class for Vector Embedding providers in PathFinder AI.

    Business logic services and repositories must strictly depend on this interface
    rather than any concrete third-party SDK (OpenAI, local models, etc.).
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Configured vector embedding dimension."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate vector embedding for a single search query."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a batch of documents."""
        pass
