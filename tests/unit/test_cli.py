import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from autonomous_dataops.cli import app

runner = CliRunner()


def isolated_config(tmp_path: Path) -> Path:
    data = yaml.safe_load(Path("config/default.yaml").read_text(encoding="utf-8"))
    data["workflow"]["state_directory"] = str(tmp_path / "state")
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_cli_run_writes_typed_result_and_checkpoint(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    config = isolated_config(tmp_path)
    result = runner.invoke(
        app,
        [
            "run",
            "examples/sample_input.json",
            "--config",
            str(config),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "COMPLETED"
    assert payload["execution"] == {"dry_run": True, "provider": "mock"}
    assert (tmp_path / "state" / f"{payload['run_id']}.json").exists()


def test_cli_configuration_and_health_commands(tmp_path: Path) -> None:
    config = isolated_config(tmp_path)
    validated = runner.invoke(app, ["validate-config", "--config", str(config)])
    shown = runner.invoke(app, ["show-config", "--config", str(config)])
    versioned = runner.invoke(app, ["version"])
    diagnosed = runner.invoke(app, ["doctor"])
    assert validated.exit_code == shown.exit_code == versioned.exit_code == diagnosed.exit_code == 0
    assert "Valid" in validated.output
    assert '"provider"' in shown.output
    assert "0.1.0" in versioned.output
    assert "OK" in diagnosed.output


def test_cli_rejects_unsupported_provider(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "run",
            "examples/sample_input.json",
            "--provider",
            "vendor",
            "--output",
            str(tmp_path / "x"),
        ],
    )
    assert result.exit_code != 0
    assert "Only the mock provider" in result.output
