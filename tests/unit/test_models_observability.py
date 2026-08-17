import json
import logging

import pytest
from pydantic import ValidationError

from autonomous_dataops.models import IncidentInput, RiskAssessment, RunState, StageResult
from autonomous_dataops.observability import log_event
from autonomous_dataops.providers.mock import MockProvider


def test_models_reject_unknown_fields_and_invalid_probability() -> None:
    with pytest.raises(ValidationError):
        IncidentInput(case_id="x", title="t", description="d", unexpected=True)
    with pytest.raises(ValidationError):
        RiskAssessment(probability=1.1)


def test_run_state_rejects_duplicate_stage_names() -> None:
    provider = MockProvider()
    common = {
        "stage": "observe",
        "agent": "observer",
        "summary": "done",
        "rationale": "validated",
        "usage": provider.usage_metadata(),
    }
    with pytest.raises(ValidationError, match="duplicate"):
        RunState(
            incident=IncidentInput(case_id="x", title="t", description="d"),
            stages=[StageResult(**common), StageResult(**common)],
        )


def test_structured_log_redacts_sensitive_fields(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="autonomous_dataops"):
        log_event("approval_checked", run_id="r1", token="secret-value", nested={"password": "x"})
    record = json.loads(caplog.messages[-1])
    assert record["event"] == "approval_checked"
    assert record["token"] == "[REDACTED]"
    assert record["nested"]["password"] == "[REDACTED]"
