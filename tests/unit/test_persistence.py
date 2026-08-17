from pathlib import Path
from unittest.mock import patch

import pytest

from autonomous_dataops.models import IncidentInput, RunState
from autonomous_dataops.persistence import JsonRunStateRepository


def state() -> RunState:
    return RunState(
        run_id="safe-run_01",
        incident=IncidentInput(case_id="case", title="Title", description="Description"),
    )


def test_json_repository_round_trip(tmp_path: Path) -> None:
    repository = JsonRunStateRepository(tmp_path)
    original = state()
    repository.save(original)
    loaded = repository.load("safe-run_01")
    assert loaded == original


def test_json_repository_returns_none_for_missing_run(tmp_path: Path) -> None:
    assert JsonRunStateRepository(tmp_path).load("missing") is None


def test_json_repository_rejects_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsafe path"):
        JsonRunStateRepository(tmp_path).load("../secret")


def test_json_repository_retries_transient_replace_lock(tmp_path: Path) -> None:
    repository = JsonRunStateRepository(tmp_path, retry_delay_seconds=0)
    real_replace = __import__("os").replace
    attempts = 0

    def flaky_replace(source: Path, destination: Path) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise PermissionError("temporarily locked")
        real_replace(source, destination)

    with patch("autonomous_dataops.persistence.os.replace", side_effect=flaky_replace):
        repository.save(state())
    assert attempts == 2
    assert repository.load("safe-run_01") is not None
