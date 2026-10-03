from __future__ import annotations

import json
import socket

import pytest
from typer.testing import CliRunner

from goldscope import __version__
from goldscope.cli import app

runner = CliRunner()
FAKE_KEY = "synthetic-test-key-123"  # synthetic


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_lists_target_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("doctor", "sources", "collect", "backtest", "train", "predict", "pipeline"):
        assert name in result.output


def test_doctor_json_reports_booleans_never_secret_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", FAKE_KEY)
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0
    assert FAKE_KEY not in result.output
    report = json.loads(result.output)
    assert report["secrets_configured"]["ALPHA_VANTAGE_API_KEY"] is True
    assert report["secrets_configured"]["FRED_API_KEY"] is False


def test_doctor_without_any_config_succeeds_offline() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "app_env: local" in result.output


def test_doctor_invalid_config_exits_1_without_echoing_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "banana")
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1
    assert "APP_ENV" in result.output
    assert "banana" not in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["collect", "gold"],
        ["collect", "macro"],
        ["dataset", "build"],
        ["backtest"],
        ["train"],
        ["predict"],
        ["pipeline", "daily"],
        ["predictions", "score"],
        ["sources", "audit"],
    ],
)
def test_planned_commands_fail_explicitly_never_fake_success(args: list[str]) -> None:
    result = runner.invoke(app, args)
    assert result.exit_code == 3
    assert "not_implemented" in result.output
    assert "success" not in result.output.lower()


def test_network_guard_is_active() -> None:
    with pytest.raises(RuntimeError, match="network access is blocked"):
        socket.create_connection(("example.com", 80))
