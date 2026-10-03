"""Application settings.

Design rules (docs/CONFIGURATION_BLUEPRINT.md section 3):
- Everything is optional at load time so tests, docs and `doctor` work offline.
- A value is validated for *shape* on load, and for *presence* only when a feature needs it
  (`require_secret`).
- `.env` is never read implicitly; pass `env_file` explicitly.
- Secrets are `SecretStr`; nothing here ever prints their value.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from goldscope.core.errors import ConfigError


class AppEnv(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    app_env: AppEnv = AppEnv.LOCAL
    database_url: SecretStr | None = None
    test_database_url: SecretStr | None = None
    alpha_vantage_api_key: SecretStr | None = None
    fred_api_key: SecretStr | None = None
    api_base_url: str = "http://localhost:8000"
    data_root: Path = Path("./runtime/data")
    artifact_root: Path = Path("./runtime/artifacts")
    log_level: LogLevel = LogLevel.INFO
    display_timezone: str = "Asia/Ho_Chi_Minh"

    @field_validator("display_timezone")
    @classmethod
    def _valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("must be a valid IANA timezone name") from exc
        return value

    def secret_values(self) -> list[str]:
        """Plain secret values, for log redaction only. Never display these."""
        secrets = (
            self.database_url,
            self.test_database_url,
            self.alpha_vantage_api_key,
            self.fred_api_key,
        )
        return [s.get_secret_value() for s in secrets if s is not None]

    def configured(self) -> dict[str, bool]:
        """Which optional secrets are set (booleans only; safe to print)."""
        return {
            "DATABASE_URL": self.database_url is not None,
            "TEST_DATABASE_URL": self.test_database_url is not None,
            "ALPHA_VANTAGE_API_KEY": self.alpha_vantage_api_key is not None,
            "FRED_API_KEY": self.fred_api_key is not None,
        }


_SECRET_FIELDS = frozenset(
    {"database_url", "test_database_url", "alpha_vantage_api_key", "fred_api_key"}
)


def load_settings(env_file: Path | None = None) -> Settings:
    """Load settings from the environment, optionally from an explicit env file.

    Raises ConfigError with variable names only; invalid values are never echoed.
    """
    if env_file is not None and not env_file.is_file():
        raise ConfigError(f"env file not found: {env_file}")
    try:
        return Settings(_env_file=env_file)
    except ValidationError as exc:
        names = sorted({str(err["loc"][0]).upper() for err in exc.errors() if err["loc"]})
        raise ConfigError(f"invalid configuration for: {', '.join(names)}") from None


def require_secret(settings: Settings, field: str) -> str:
    """Return a secret needed by a feature, or fail with a clear error (no value leak)."""
    if field not in _SECRET_FIELDS:
        raise ValueError(f"{field!r} is not a secret setting")
    value: SecretStr | None = getattr(settings, field)
    if value is None:
        raise ConfigError(f"{field.upper()} is required for this command but is not set")
    return value.get_secret_value()
