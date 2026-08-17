from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RunStatus(StrEnum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvidenceInput(StrictModel):
    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    reference: str | None = None


class IncidentInput(StrictModel):
    case_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    evidence: list[EvidenceInput] = Field(default_factory=list)


class ExecutionContext(StrictModel):
    dry_run: bool = True
    provider: str = "mock"


class Evidence(StrictModel):
    source: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    reference: str | None = None


class RiskAssessment(StrictModel):
    severity: Severity = Severity.LOW
    probability: float = Field(default=0.0, ge=0.0, le=1.0)
    impact_areas: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    residual_risk: str = "unknown"
    approval_required: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class UsageMetadata(StrictModel):
    provider: str
    model: str | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    retry_count: int = Field(default=0, ge=0)


class StageResult(StrictModel):
    stage: str = Field(min_length=1)
    agent: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    evidence: list[Evidence] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    alternatives_considered: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    risk: RiskAssessment = Field(default_factory=RiskAssessment)
    usage: UsageMetadata
    completed_at: datetime = Field(default_factory=utc_now)


class RunState(StrictModel):
    schema_version: int = 1
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    project: str = "autonomous-dataops-agent"
    started_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    incident: IncidentInput
    execution: ExecutionContext = Field(default_factory=ExecutionContext)
    stages: list[StageResult] = Field(default_factory=list)
    status: RunStatus = RunStatus.RUNNING
    error: str | None = None

    @model_validator(mode="after")
    def stages_must_be_unique(self) -> RunState:
        names = [stage.stage for stage in self.stages]
        if len(names) != len(set(names)):
            raise ValueError("Workflow state cannot contain duplicate stages.")
        return self

    def add_stage(self, result: StageResult, *, updated_at: datetime | None = None) -> None:
        if any(existing.stage == result.stage for existing in self.stages):
            raise ValueError(f"Stage already completed: {result.stage}")
        self.stages.append(result)
        self.updated_at = updated_at or utc_now()


class EvalExpectation(StrictModel):
    required_stages: list[str]
    required_findings: list[str] = Field(default_factory=list)
    forbidden_findings: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    expected_risk_range: tuple[float, float] = (0.0, 1.0)
    minimum_evidence_per_stage: int = Field(default=1, ge=0)

    @model_validator(mode="after")
    def valid_risk_range(self) -> EvalExpectation:
        low, high = self.expected_risk_range
        if not 0.0 <= low <= high <= 1.0:
            raise ValueError("expected_risk_range must be ordered and between 0 and 1")
        return self


class EvalCase(StrictModel):
    case_id: str
    input: IncidentInput
    expected: EvalExpectation


JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
