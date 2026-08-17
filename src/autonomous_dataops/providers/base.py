from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from ..models import UsageMetadata

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, *, system: str, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        *,
        system: str,
        prompt: str,
        response_model: type[T],
    ) -> T:
        raise NotImplementedError

    def critique(self, *, system: str, prompt: str) -> str:
        return self.generate_text(system=system, prompt=prompt)

    def usage_metadata(self) -> UsageMetadata:
        return UsageMetadata(provider=self.__class__.__name__)
