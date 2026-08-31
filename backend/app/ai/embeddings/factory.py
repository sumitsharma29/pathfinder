from backend.app.ai.embeddings.base import EmbeddingProvider
from backend.app.ai.embeddings.mock_provider import MockEmbeddingProvider
from backend.app.ai.embeddings.openai_provider import OpenAIEmbeddingProvider
from backend.app.core.config import settings


def get_embedding_provider() -> EmbeddingProvider:
    """Factory returning configured EmbeddingProvider."""
    provider_name = (settings.EMBEDDING_PROVIDER or "mock").lower().strip()

    if provider_name == "openai":
        return OpenAIEmbeddingProvider()
    elif provider_name in ["mock", "test", "local"]:
        return MockEmbeddingProvider()
    else:
        return MockEmbeddingProvider()
