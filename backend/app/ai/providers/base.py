from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract Base Class for LLM providers in PathFinder AI.

    Business logic services must strictly depend on this interface rather than
    any concrete third-party SDK (OpenAI, Gemini, local, etc.).
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Generate free-form text response from the model."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> T:
        """Generate a response constrained and validated against a Pydantic schema."""
        pass
