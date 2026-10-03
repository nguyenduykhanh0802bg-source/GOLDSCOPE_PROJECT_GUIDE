"""Engine/session helpers and the test-database safety guard."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from pydantic import SecretStr
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session

from goldscope.core.errors import ConfigError
from goldscope.core.settings import AppEnv, Settings


def normalize_url(url: str | SecretStr) -> str:
    """Return a psycopg3 PostgreSQL URL string. Errors never echo the URL (it holds secrets)."""
    raw = url.get_secret_value() if isinstance(url, SecretStr) else url
    try:
        parsed = make_url(raw)
    except ArgumentError:
        raise ConfigError("database URL is not a valid SQLAlchemy URL") from None
    if parsed.get_backend_name() != "postgresql":
        raise ConfigError("database URL must use PostgreSQL")
    if parsed.drivername == "postgresql":
        parsed = parsed.set(drivername="postgresql+psycopg")
    return parsed.render_as_string(hide_password=False)


def create_db_engine(url: str | SecretStr) -> Engine:
    return create_engine(normalize_url(url), pool_pre_ping=True)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    """One transaction: commit on success, roll back everything on any exception."""
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def resolve_test_database_url(settings: Settings) -> str:
    """The URL integration tests may use. Refuses anything that could be a real database."""
    if settings.test_database_url is None:
        raise ConfigError("TEST_DATABASE_URL is required for database tests but is not set")
    test_url = normalize_url(settings.test_database_url)
    if settings.database_url is not None and test_url == normalize_url(settings.database_url):
        raise ConfigError("TEST_DATABASE_URL must differ from DATABASE_URL")
    if settings.app_env is AppEnv.PRODUCTION:
        raise ConfigError("database tests must not run with APP_ENV=production")
    name = make_url(test_url).database or ""
    if "test" not in name.lower():
        raise ConfigError("TEST_DATABASE_URL database name must contain 'test'")
    return test_url
