from pathlib import Path

import pytest
from pydantic import ValidationError

from autonomous_dataops.config import load_config

DEFAULT_CONFIG = Path("config/default.yaml")


def test_default_config_is_valid() -> None:
    settings = load_config(DEFAULT_CONFIG, environment={})
    assert settings.provider.name == "mock"
    assert settings.workflow.checkpoint_each_stage is True


def test_environment_override_is_typed() -> None:
    settings = load_config(
        DEFAULT_CONFIG,
        environment={
            "DATAOPS__PROVIDER__MAX_RETRIES": "5",
            "DATAOPS__TOOLS__ALLOW_MUTATIONS": "false",
        },
    )
    assert settings.provider.max_retries == 5
    assert settings.tools.allow_mutations is False


def test_unknown_config_key_fails_fast(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    content = DEFAULT_CONFIG.read_text().rstrip()
    path.write_text(content[:-1] + ', "unknown": true}', encoding="utf-8")
    with pytest.raises((ValidationError, ValueError)):
        load_config(path, environment={})


def test_unsafe_approval_configuration_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Mutations cannot be enabled"):
        load_config(
            DEFAULT_CONFIG,
            environment={
                "DATAOPS__TOOLS__ALLOW_MUTATIONS": "true",
                "DATAOPS__APPROVAL__MODE": "disabled",
            },
        )
