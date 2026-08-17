from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    ok: bool
    data: dict[str, Any] = Field(default_factory=dict)
    audit: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BaseTool(ABC):
    name: str
    mutating: bool = False

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        raise NotImplementedError
