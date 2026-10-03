from __future__ import annotations

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect, text

from goldscope.db.models import Base

from .conftest import alembic_config, reset_schema

EXPECTED_TABLES = {
    "data_sources",
    "ingestion_runs",
    "raw_objects",
    "market_observations",
    "macro_series",
    "macro_observations",
    "data_quality_events",
}


def tables(engine: Engine) -> set[str]:
    return set(inspect(engine).get_table_names()) - {"alembic_version"}


def test_clean_database_upgrades_to_head(engine: Engine, test_url: str) -> None:
    reset_schema(engine)
    assert tables(engine) == set()
    command.upgrade(alembic_config(test_url), "head")
    assert tables(engine) == EXPECTED_TABLES
    head = ScriptDirectory.from_config(alembic_config(test_url)).get_current_head()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == head


def test_models_match_migrations_no_autogenerate_drift(engine: Engine) -> None:
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True})
        assert compare_metadata(ctx, Base.metadata) == []


def test_downgrade_to_base_then_upgrade_again(engine: Engine, test_url: str) -> None:
    cfg = alembic_config(test_url)
    command.downgrade(cfg, "base")
    assert tables(engine) == set()
    command.upgrade(cfg, "head")
    assert tables(engine) == EXPECTED_TABLES


def test_single_linear_history() -> None:
    script = ScriptDirectory.from_config(alembic_config("postgresql+psycopg://x/y_test"))
    assert len(script.get_heads()) == 1


def test_timestamps_are_timestamptz_and_values_unconstrained_numeric(engine: Engine) -> None:
    cols = {
        (c["table_name"], c["column_name"]): c
        for c in _columns(engine)
        if c["column_name"]
        in {"started_at", "ended_at", "fetched_at", "available_at", "ingested_at", "price", "value"}
    }
    for (_, name), c in cols.items():
        if name in {"price", "value"}:
            assert c["data_type"] == "numeric"
            assert c["numeric_precision"] is None  # precision chosen after source audit
        else:
            assert c["data_type"] == "timestamp with time zone", (name, c["data_type"])


def _columns(engine: Engine) -> list[dict[str, object]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT table_name, column_name, data_type, numeric_precision "
                "FROM information_schema.columns WHERE table_schema='public'"
            )
        ).mappings()
        return [dict(r) for r in rows]
