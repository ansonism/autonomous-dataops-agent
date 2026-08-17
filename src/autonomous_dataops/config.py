from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

ENV_PREFIX = "DATAOPS__"


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AppConfig(ConfigModel):
    name: str = Field(min_length=1)
    environment: str = Field(min_length=1)


class ProviderConfig(ConfigModel):
    name: str = "mock"
    model: str = "mock-v1"
    timeout_seconds: float = Field(default=30, gt=0)
    max_retries: int = Field(default=2, ge=0)


class WorkflowConfig(ConfigModel):
    stages: list[str] = Field(min_length=1)
    checkpoint_each_stage: bool = True
    state_directory: Path = Path("out/state")

    @model_validator(mode="after")
    def unique_stages(self) -> WorkflowConfig:
        if len(self.stages) != len(set(self.stages)):
            raise ValueError("workflow.stages must not contain duplicates")
        return self


class RiskConfig(ConfigModel):
    default_approval_threshold: str = "HIGH"


class ApprovalConfig(ConfigModel):
    mode: str = "manual"
    required_for_mutations: bool = True


class ObservabilityConfig(ConfigModel):
    log_level: str = "INFO"
    structured: bool = True


class ToolsConfig(ConfigModel):
    mode: str = "fake"
    allow_mutations: bool = False


class Settings(ConfigModel):
    app: AppConfig
    provider: ProviderConfig
    workflow: WorkflowConfig
    risk: RiskConfig
    approval: ApprovalConfig
    observability: ObservabilityConfig
    tools: ToolsConfig

    @model_validator(mode="after")
    def safe_defaults(self) -> Settings:
        if self.tools.allow_mutations and self.approval.mode == "disabled":
            raise ValueError("Mutations cannot be enabled when approval is disabled")
        return self


def _parse_env_value(value: str) -> Any:
    return yaml.safe_load(value)


def _apply_environment(data: dict[str, Any], environment: Mapping[str, str]) -> None:
    for name, value in environment.items():
        if not name.startswith(ENV_PREFIX):
            continue
        path = name[len(ENV_PREFIX) :].lower().split("__")
        cursor = data
        for key in path[:-1]:
            child = cursor.setdefault(key, {})
            if not isinstance(child, dict):
                raise ValueError(f"Environment override conflicts at {name}")
            cursor = child
        cursor[path[-1]] = _parse_env_value(value)


def load_config(path: Path, *, environment: Mapping[str, str] | None = None) -> Settings:
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a mapping.")
    data = dict(raw)
    _apply_environment(data, os.environ if environment is None else environment)
    return Settings.model_validate(data)
