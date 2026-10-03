"""Command line interface.

GS-003 scope: `--version`, `doctor`, and explicit not-implemented placeholders for the
planned command surface. Placeholders never print success; they exit with code 3.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Annotated

import typer

from goldscope import __version__
from goldscope.core.errors import ConfigError, NotImplementedYetError
from goldscope.core.logging import configure_logging, redact_text
from goldscope.core.settings import Settings, load_settings

EXIT_OK = 0
EXIT_CONFIG = 1
EXIT_NOT_IMPLEMENTED = 3

app = typer.Typer(
    name="goldscope",
    help="GoldScope - gold market research and forecasting platform.",
    no_args_is_help=True,
    add_completion=False,
)
sources_app = typer.Typer(help="Data source operations.", no_args_is_help=True)
collect_app = typer.Typer(help="Collect data from providers.", no_args_is_help=True)
dataset_app = typer.Typer(help="Dataset snapshots.", no_args_is_help=True)
pipeline_app = typer.Typer(help="Scheduled pipelines.", no_args_is_help=True)
predictions_app = typer.Typer(help="Issued predictions.", no_args_is_help=True)
app.add_typer(sources_app, name="sources")
app.add_typer(collect_app, name="collect")
app.add_typer(dataset_app, name="dataset")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(predictions_app, name="predictions")

EnvFileOption = Annotated[
    Path | None,
    typer.Option("--env-file", help="Explicit env file to load. .env is never loaded implicitly."),
]


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"goldscope {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show version."),
    ] = False,
) -> None:
    """GoldScope command line."""


def _load(env_file: Path | None) -> Settings:
    try:
        settings = load_settings(env_file)
    except ConfigError as exc:
        typer.echo(f"error[{exc.code}]: {exc.message}", err=True)
        raise typer.Exit(EXIT_CONFIG) from None
    configure_logging(settings.log_level.value, settings.secret_values())
    return settings


@app.command()
def doctor(
    env_file: EnvFileOption = None,
    as_json: Annotated[bool, typer.Option("--json", help="Machine-readable output.")] = False,
) -> None:
    """Offline environment check. Makes no network calls and prints no secret values."""
    settings = _load(env_file)
    report = {
        "goldscope": __version__,
        "python": platform.python_version(),
        "python_ok": sys.version_info[:2] == (3, 12),
        "platform": platform.system(),
        "app_env": settings.app_env.value,
        "log_level": settings.log_level.value,
        "display_timezone": settings.display_timezone,
        "data_root": str(settings.data_root),
        "artifact_root": str(settings.artifact_root),
        "secrets_configured": settings.configured(),
    }
    if as_json:
        typer.echo(json.dumps(report, indent=2))
    else:
        for key, value in report.items():
            typer.echo(f"{key}: {value}")
        if not report["python_ok"]:
            typer.echo("warning: project targets Python 3.12", err=True)


def _not_implemented(command: str, task: str) -> None:
    err = NotImplementedYetError(f"`{command}` is not implemented yet (planned in {task}).")
    typer.echo(redact_text(f"error[{err.code}]: {err.message}"), err=True)
    raise typer.Exit(EXIT_NOT_IMPLEMENTED)


@sources_app.command("audit")
def sources_audit() -> None:
    """(GS-001) Audit data sources. For now use: python lab00/scripts/audit_sources.py."""
    _not_implemented("sources audit", "GS-001")


@collect_app.command("gold")
def collect_gold() -> None:
    """(GS-005) Collect gold prices."""
    _not_implemented("collect gold", "GS-005")


@collect_app.command("macro")
def collect_macro() -> None:
    """(GS-012) Collect macro series."""
    _not_implemented("collect macro", "GS-012")


@dataset_app.command("build")
def dataset_build() -> None:
    """(GS-006/007) Build dataset snapshot."""
    _not_implemented("dataset build", "GS-006/GS-007")


@app.command()
def backtest() -> None:
    """(GS-008) Walk-forward backtest."""
    _not_implemented("backtest", "GS-008")


@app.command()
def train() -> None:
    """(GS-009) Train models."""
    _not_implemented("train", "GS-009")


@app.command()
def predict() -> None:
    """(GS-010) Issue predictions."""
    _not_implemented("predict", "GS-010")


@pipeline_app.command("daily")
def pipeline_daily() -> None:
    """(GS-013) Daily pipeline."""
    _not_implemented("pipeline daily", "GS-013")


@predictions_app.command("score")
def predictions_score() -> None:
    """(GS-013) Score due predictions."""
    _not_implemented("predictions score", "GS-013")
