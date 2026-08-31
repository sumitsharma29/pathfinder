import logging
from typing import List, Optional
from backend.app.ai.embeddings.base import EmbeddingProvider
from backend.app.core.config import settings
from backend.app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Production OpenAI Embedding Provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dimension: int = settings.EMBEDDING_DIMENSION
    ):
        self.api_key = api_key or settings.EMBEDDING_API_KEY
        self.model = model or settings.EMBEDDING_MODEL or "text-embedding-3-small"
        self._dimension = dimension
        self.timeout = settings.AI_TIMEOUT_SECONDS or 30

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_query(self, text: str) -> List[float]:
        res = await self.embed_documents([text])
        return res[0]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise AppException(
                status_code=503,
                code="EMBEDDING_PROVIDER_UNCONFIGURED",
                message="Embedding API key is not configured."
            )

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "input": texts,
                "dimensions": self._dimension
            }

            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json=payload
                )

                if resp.status_code != 200:
                    logger.error(f"OpenAI embedding error ({resp.status_code}): {resp.text}")
                    raise AppException(
                        status_code=502,
                        code="EMBEDDING_PROVIDER_ERROR",
                        message="Upstream embedding provider returned an error."
                    )

                data = resp.json()
                return [item["embedding"] for item in data["data"]]
        except httpx.TimeoutException:
            logger.error("OpenAI embedding request timed out.")
            raise AppException(
                status_code=504,
                code="EMBEDDING_PROVIDER_TIMEOUT",
                message="Embedding provider request timed out."
            )
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            logger.error(f"Unexpected OpenAI embedding error: {str(e)}")
            raise AppException(
                status_code=502,
                code="EMBEDDING_PROVIDER_UNAVAILABLE",
                message="Failed to communicate with embedding provider."
            )
