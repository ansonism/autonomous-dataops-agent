from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path

from .models import RunState


class RunStateRepository(ABC):
    @abstractmethod
    def save(self, state: RunState) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, run_id: str) -> RunState | None:
        raise NotImplementedError


class InMemoryRunStateRepository(RunStateRepository):
    def __init__(self) -> None:
        self._states: dict[str, str] = {}

    def save(self, state: RunState) -> None:
        self._states[state.run_id] = state.model_dump_json()

    def load(self, run_id: str) -> RunState | None:
        payload = self._states.get(run_id)
        return RunState.model_validate_json(payload) if payload is not None else None


class JsonRunStateRepository(RunStateRepository):
    """Local atomic JSON checkpoints; run identifiers never become arbitrary paths."""

    def __init__(
        self,
        directory: Path,
        *,
        replace_attempts: int = 5,
        retry_delay_seconds: float = 0.05,
    ) -> None:
        self.directory = directory
        self.replace_attempts = replace_attempts
        self.retry_delay_seconds = retry_delay_seconds

    def _path(self, run_id: str) -> Path:
        safe_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        if not run_id or any(character not in safe_characters for character in run_id):
            raise ValueError("run_id contains unsafe path characters")
        return self.directory / f"{run_id}.json"

    def save(self, state: RunState) -> None:
        path = self._path(state.run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        for attempt in range(self.replace_attempts):
            try:
                os.replace(temporary, path)
                return
            except PermissionError:
                if attempt + 1 == self.replace_attempts:
                    raise
                time.sleep(self.retry_delay_seconds)

    def load(self, run_id: str) -> RunState | None:
        path = self._path(run_id)
        if not path.exists():
            return None
        return RunState.model_validate_json(path.read_text(encoding="utf-8"))
