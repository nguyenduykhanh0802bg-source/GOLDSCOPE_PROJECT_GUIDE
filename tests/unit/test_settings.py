from __future__ import annotations

from pathlib import Path

import pytest

from goldscope.core.errors import ConfigError
from goldscope.core.settings import AppEnv, load_settings, require_secret

FAKE_KEY = "synthetic-test-key-123"  # synthetic value, not a real credential


def test_defaults_load_offline_without_any_keys() -> None:
    s = load_settings()
    assert s.app_env is AppEnv.LOCAL
    assert s.display_timezone == "Asia/Ho_Chi_Minh"
    assert not any(s.configured().values())


def test_env_vars_are_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s = load_settings()
    assert s.app_env is AppEnv.TEST
    assert s.log_level.value == "DEBUG"


def test_empty_values_in_env_example_style_are_treated_as_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    assert load_settings().database_url is None


def test_invalid_enum_error_names_variable_not_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "banana")
    with pytest.raises(ConfigError) as info:
        load_settings()
    assert "APP_ENV" in info.value.message
    assert "banana" not in info.value.message


def test_invalid_timezone_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISPLAY_TIMEZONE", "Mars/Olympus")
    with pytest.raises(ConfigError, match="DISPLAY_TIMEZONE"):
        load_settings()


def test_require_secret_missing_gives_clear_error() -> None:
    with pytest.raises(ConfigError, match="ALPHA_VANTAGE_API_KEY is required"):
        require_secret(load_settings(), "alpha_vantage_api_key")


def test_require_secret_returns_value_but_repr_hides_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", FAKE_KEY)
    s = load_settings()
    assert require_secret(s, "alpha_vantage_api_key") == FAKE_KEY
    assert FAKE_KEY not in repr(s)
    assert FAKE_KEY not in str(s.model_dump())


def test_require_secret_rejects_non_secret_field() -> None:
    with pytest.raises(ValueError, match="not a secret"):
        require_secret(load_settings(), "app_env")


def test_env_file_only_loaded_when_explicit(tmp_path: Path) -> None:
    env = tmp_path / "custom.env"
    env.write_text(f"FRED_API_KEY={FAKE_KEY}\n", encoding="utf-8")
    assert load_settings().fred_api_key is None
    assert load_settings(env).fred_api_key is not None


def test_missing_env_file_is_config_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="env file not found"):
        load_settings(tmp_path / "nope.env")
