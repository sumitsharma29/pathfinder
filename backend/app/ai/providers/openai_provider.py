import json
import logging
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError

from backend.app.ai.providers.base import LLMProvider
from backend.app.core.config import settings
from backend.app.core.exceptions import AppException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenAILLMProvider(LLMProvider):
    """OpenAI API Provider implementation for PathFinder AI."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL or "gpt-4o-mini"
        self.timeout = settings.AI_TIMEOUT_SECONDS or 30

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        if not self.api_key:
            raise AppException(
                status_code=503,
                code="LLM_PROVIDER_UNCONFIGURED",
                message="OpenAI API key is not configured."
            )

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else settings.AI_TEMPERATURE,
                "max_tokens": max_tokens if max_tokens is not None else settings.AI_MAX_TOKENS
            }

            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )

                if resp.status_code != 200:
                    logger.error(f"OpenAI API error ({resp.status_code}): {resp.text}")
                    raise AppException(
                        status_code=502,
                        code="LLM_PROVIDER_ERROR",
                        message="Upstream AI provider returned an error."
                    )

                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            logger.error("OpenAI request timed out.")
            raise AppException(
                status_code=504,
                code="LLM_PROVIDER_TIMEOUT",
                message="AI provider request timed out."
            )
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            logger.error(f"Unexpected OpenAI error: {str(e)}")
            raise AppException(
                status_code=502,
                code="LLM_PROVIDER_UNAVAILABLE",
                message="Failed to communicate with AI provider."
            )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> T:
        raw_text = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Parse JSON
        try:
            # Strip potential markdown fences
            clean_json = raw_text.strip()
            if clean_json.startswith("```"):
                lines = clean_json.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_json = "\n".join(lines).strip()

            data = json.loads(clean_json)
            return response_schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to parse structured LLM response: {str(e)}")
            raise AppException(
                status_code=502,
                code="LLM_INVALID_STRUCTURED_OUTPUT",
                message="AI provider returned malformed structured output."
            )
