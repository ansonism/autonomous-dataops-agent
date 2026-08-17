from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from ..models import UsageMetadata
from .base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class MockProvider(BaseLLMProvider):
    """Deterministic provider used for local development, CI and eval fixtures."""

    def generate_text(self, *, system: str, prompt: str) -> str:
        del system
        return f"Mock analysis: {prompt[:160]}"

    def generate_structured(
        self,
        *,
        system: str,
        prompt: str,
        response_model: type[T],
    ) -> T:
        del system, prompt
        return response_model.model_validate({})

    def usage_metadata(self) -> UsageMetadata:
        return UsageMetadata(
            provider="mock", model="mock-v1", input_tokens=0, output_tokens=0
        )
