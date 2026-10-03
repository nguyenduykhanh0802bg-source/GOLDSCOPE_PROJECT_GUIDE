"""PostgreSQL integration fixtures. Requires TEST_DATABASE_URL (a dedicated test database).

The schema is rebuilt from scratch through Alembic once per session; rows are truncated
between tests. Tests are skipped, never faked, when no test database is configured.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text

from goldscope.core.errors import ConfigError
from goldscope.core.settings import load_settings
from goldscope.db.models import Base
from goldscope.db.session import create_db_engine, resolve_test_database_url

ROOT = Path(__file__).resolve().parents[2]


def alembic_config(url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return cfg


@pytest.fixture(scope="session")
def test_url() -> str:
    try:
        return resolve_test_database_url(load_settings())
    except ConfigError as exc:
        if "is required" in exc.message:
            pytest.skip("TEST_DATABASE_URL not set; PostgreSQL integration tests not run")
        raise


def reset_schema(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture(scope="session")
def engine(test_url: str) -> Iterator[Engine]:
    eng = create_db_engine(test_url)
    reset_schema(eng)
    command.upgrade(alembic_config(test_url), "head")
    yield eng
    eng.dispose()


@pytest.fixture(autouse=True)
def _truncate(engine: Engine) -> Iterator[None]:
    yield
    tables = ", ".join(Base.metadata.tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} CASCADE"))
