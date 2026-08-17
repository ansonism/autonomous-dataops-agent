from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich import print

from . import __version__
from .config import Settings, load_config
from .models import ExecutionContext, IncidentInput
from .observability import configure_logging
from .persistence import JsonRunStateRepository
from .providers.mock import MockProvider
from .workflow import Workflow

app = typer.Typer(help="Autonomous DataOps Agent")


@app.command()
def run(
    input_file: Annotated[Path, typer.Argument(exists=True, readable=True)],
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("out/result.json"),
    config: Annotated[Path, typer.Option("--config")] = Path("config/default.yaml"),
    provider: Annotated[str, typer.Option("--provider")] = "mock",
    dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = True,
) -> None:
    """Run the typed workflow against a JSON incident input."""
    if provider != "mock":
        raise typer.BadParameter("Only the mock provider is implemented in Phase 1.")
    settings = load_config(config)
    configure_logging(settings.observability.log_level)
    try:
        incident = IncidentInput.model_validate_json(input_file.read_text(encoding="utf-8"))
    except ValidationError as error:
        raise typer.BadParameter(f"Invalid incident input: {error}") from error
    repository = JsonRunStateRepository(settings.workflow.state_directory)
    state = Workflow(
        MockProvider(),
        stages=settings.workflow.stages,
        repository=repository,
        checkpoint_each_stage=settings.workflow.checkpoint_each_stage,
    ).run(incident, ExecutionContext(dry_run=dry_run, provider=provider))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]Completed[/green] {state.run_id} -> {output}")


@app.command("validate-config")
def validate_config(
    config: Annotated[Path, typer.Option("--config")] = Path("config/default.yaml"),
) -> None:
    _ = load_config(config)
    print(
        "[green]Valid[/green] configuration with sections: "
        f"{', '.join(Settings.model_fields)}"
    )


@app.command("show-config")
def show_config(
    config: Annotated[Path, typer.Option("--config")] = Path("config/default.yaml"),
) -> None:
    print_json = json.dumps(load_config(config).model_dump(mode="json"), indent=2)
    print(print_json)


@app.command()
def version() -> None:
    print(__version__)


@app.command()
def doctor() -> None:
    print("[green]OK[/green] core scaffold imports and mock provider are available.")


if __name__ == "__main__":
    app()
