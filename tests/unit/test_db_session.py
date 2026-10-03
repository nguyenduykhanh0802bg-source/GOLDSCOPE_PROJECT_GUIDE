from __future__ import annotations

import pytest

from goldscope.core.errors import ConfigError
from goldscope.core.settings import Settings
from goldscope.db.session import normalize_url, resolve_test_database_url

DEV = "postgresql+psycopg://u:pw@localhost:5432/goldscope_dev"  # synthetic
TEST = "postgresql+psycopg://u:pw@localhost:5432/goldscope_test"  # synthetic


def make(**kw: object) -> Settings:
    return Settings(**kw)  # type: ignore[arg-type]


def test_plain_postgresql_scheme_is_upgraded_to_psycopg3() -> None:
    assert normalize_url("postgresql://u:pw@h/db").startswith("postgresql+psycopg://")


def test_non_postgres_url_is_rejected_without_echo() -> None:
    with pytest.raises(ConfigError) as info:
        normalize_url("sqlite:///secret-path.db")
    assert "secret-path" not in info.value.message


def test_garbage_url_is_rejected_without_echo() -> None:
    with pytest.raises(ConfigError) as info:
        normalize_url("not a url pw=hunter2")
    assert "hunter2" not in info.value.message


def test_test_url_required() -> None:
    with pytest.raises(ConfigError, match="TEST_DATABASE_URL is required"):
        resolve_test_database_url(make())


def test_test_url_must_differ_from_database_url() -> None:
    with pytest.raises(ConfigError, match="must differ"):
        resolve_test_database_url(make(database_url=TEST, test_database_url=TEST))


def test_test_url_name_must_contain_test() -> None:
    with pytest.raises(ConfigError, match="must contain 'test'"):
        resolve_test_database_url(make(database_url=TEST, test_database_url=DEV))


def test_production_env_refused() -> None:
    with pytest.raises(ConfigError, match="production"):
        resolve_test_database_url(make(app_env="production", test_database_url=TEST))


def test_valid_test_url_accepted() -> None:
    assert resolve_test_database_url(make(database_url=DEV, test_database_url=TEST)) == TEST
