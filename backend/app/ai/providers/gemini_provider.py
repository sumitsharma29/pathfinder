import json
import logging
import asyncio
import urllib.request
import urllib.error
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError

from backend.app.ai.providers.base import LLMProvider
from backend.app.core.config import settings
from backend.app.core.exceptions import AppException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GeminiLLMProvider(LLMProvider):
    """Google Gemini API Provider for PathFinder AI (supports gemini-3.6-flash, gemini-3.7-flash, etc.)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL or "gemini-3.6-flash"
        self.timeout = settings.AI_TIMEOUT_SECONDS or 30

    def _sync_post(self, url: str, payload: dict, timeout: float) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"Gemini API error ({e.code}): {err_body}")
            raise AppException(
                status_code=502,
                code="LLM_PROVIDER_ERROR",
                message=f"Gemini API error: {err_body[:200]}"
            )
        except urllib.error.URLError as e:
            logger.error(f"Gemini connection error: {e}")
            raise AppException(
                status_code=504,
                code="LLM_PROVIDER_TIMEOUT",
                message=f"Gemini connection failed: {e.reason}"
            )
        except Exception as e:
            logger.error(f"Gemini unexpected error: {e}")
            raise AppException(
                status_code=502,
                code="LLM_PROVIDER_UNAVAILABLE",
                message=f"Failed to communicate with Google Gemini API: {str(e)}"
            )

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
                message="Google Gemini API key is not configured in LLM_API_KEY."
            )

        model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER REQUEST:\n{prompt}"}]
            })
        else:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature if temperature is not None else settings.AI_TEMPERATURE,
            }
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        data = await asyncio.to_thread(self._sync_post, url, payload, float(self.timeout))

        candidates = data.get("candidates", [])
        if not candidates:
            raise AppException(
                status_code=502,
                code="LLM_EMPTY_RESPONSE",
                message="Gemini returned no candidate responses."
            )

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return ""
        return parts[0].get("text", "")

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> T:
        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        augmented_system_prompt = (
            (system_prompt + "\n\n" if system_prompt else "")
            + f"CRITICAL: You must return strictly valid JSON matching this exact schema:\n{schema_json}\nDo not include any markdown fences or conversational text outside the raw JSON object."
        )

        raw_text = await self.generate(
            prompt=prompt,
            system_prompt=augmented_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        try:
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
            logger.error(f"Failed to parse structured Gemini LLM response: {str(e)}\nRaw output: {raw_text}")
            raise AppException(
                status_code=502,
                code="LLM_INVALID_STRUCTURED_OUTPUT",
                message="Gemini returned malformed structured output."
            )
