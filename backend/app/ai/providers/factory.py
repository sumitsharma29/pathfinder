from backend.app.ai.providers.base import LLMProvider
from backend.app.ai.providers.mock_provider import MockLLMProvider
from backend.app.ai.providers.openai_provider import OpenAILLMProvider
from backend.app.ai.providers.gemini_provider import GeminiLLMProvider
from backend.app.core.config import settings


def get_llm_provider() -> LLMProvider:
    """Factory function returning the configured LLMProvider instance."""
    provider_name = (settings.LLM_PROVIDER or "mock").lower().strip()

    if provider_name in ["gemini", "google"]:
        return GeminiLLMProvider()
    elif provider_name == "openai":
        return OpenAILLMProvider()
    elif provider_name in ["mock", "test", "local"]:
        return MockLLMProvider()
    else:
        # Default fallback to MockLLMProvider for offline resiliency
        return MockLLMProvider()
