"""Schema constraints on a real PostgreSQL. Values are synthetic test data, not GOLD prices."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import Engine, delete, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from goldscope.db.models import (
    DataQualityEvent,
    DataSource,
    IngestionRun,
    MacroObservation,
    MacroSeries,
    MarketObservation,
    RawObject,
)

T0 = datetime(2026, 1, 5, 12, 0, tzinfo=UTC)
SHA = "a" * 64


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as s:
        yield s
        s.rollback()


@pytest.fixture
def source(session: Session) -> DataSource:
    src = DataSource(provider="synthetic", dataset_key="test_series")
    session.add(src)
    session.commit()
    return src


def market(source: DataSource, **overrides: Any) -> MarketObservation:
    base: dict[str, Any] = {
        "asset_id": "TEST_ASSET",
        "source_id": source.id,
        "observation_date": date(2026, 1, 5),
        "price": Decimal("100.5"),
        "currency": "XXX",
        "unit": "test-unit",
        "price_definition": "synthetic",
        "revision_key": "r1",
        "availability_basis": "first_seen",
        "available_at": T0,
    }
    base.update(overrides)
    return MarketObservation(**base)


def rejected(session: Session, row: object) -> None:
    session.add(row)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


# ---- market observations -------------------------------------------------------------------


def test_duplicate_business_key_is_rejected(session: Session, source: DataSource) -> None:
    session.add(market(source))
    session.commit()
    rejected(session, market(source, price=Decimal("101")))


def test_new_revision_of_same_day_is_stored_and_old_kept(
    session: Session, source: DataSource
) -> None:
    session.add_all([market(source), market(source, revision_key="r2", price=Decimal("101"))])
    session.commit()
    rows = session.execute(select(MarketObservation.revision_key)).scalars().all()
    assert sorted(rows) == ["r1", "r2"]


@pytest.mark.parametrize("bad", ["0", "-1", "NaN", "Infinity", "-Infinity"])
def test_gold_price_must_be_positive_and_finite(
    session: Session, source: DataSource, bad: str
) -> None:
    rejected(session, market(source, price=Decimal(bad)))


def test_empty_revision_key_rejected(session: Session, source: DataSource) -> None:
    rejected(session, market(source, revision_key=""))


def test_null_revision_key_rejected(session: Session, source: DataSource) -> None:
    rejected(session, market(source, revision_key=None))


def test_empty_asset_rejected(session: Session, source: DataSource) -> None:
    rejected(session, market(source, asset_id=""))


def test_known_availability_requires_available_at(session: Session, source: DataSource) -> None:
    rejected(session, market(source, availability_basis="verified", available_at=None))


def test_unknown_availability_may_lack_available_at(session: Session, source: DataSource) -> None:
    session.add(market(source, availability_basis="unknown", available_at=None))
    session.commit()


def test_invalid_availability_basis_rejected(session: Session, source: DataSource) -> None:
    rejected(session, market(source, availability_basis="guessed"))


def test_numeric_roundtrip_is_exact(session: Session, source: DataSource) -> None:
    exact = Decimal("2345.123456789012345678")
    session.add(market(source, price=exact))
    session.commit()
    session.expire_all()
    assert session.execute(select(MarketObservation.price)).scalar_one() == exact


def test_timestamptz_preserves_instant_across_offsets(session: Session, source: DataSource) -> None:
    plus7 = timezone(timedelta(hours=7))
    local = datetime(2026, 1, 5, 19, 0, tzinfo=plus7)  # same instant as 12:00 UTC
    session.add(market(source, available_at=local))
    session.commit()
    session.expire_all()
    stored = session.execute(select(MarketObservation.available_at)).scalar_one()
    assert stored is not None and stored.tzinfo is not None
    assert stored == T0
    assert stored.utcoffset() == timedelta(0)  # session timezone is UTC


def test_naive_datetime_is_not_silently_accepted_as_utc(
    session: Session, source: DataSource
) -> None:
    """psycopg sends naive values as timestamp; PostgreSQL then applies the *session* zone.
    Application code must always pass aware datetimes - this documents the hazard."""
    session.execute(text("SET LOCAL TIME ZONE 'Asia/Ho_Chi_Minh'"))
    session.add(market(source, available_at=datetime(2026, 1, 5, 12, 0)))
    session.flush()
    stored = session.execute(select(MarketObservation.available_at)).scalar_one()
    assert stored != T0  # interpreted in +07:00, not UTC
    session.rollback()


# ---- referential integrity ---------------------------------------------------------------


def test_cannot_delete_source_with_observations(session: Session, source: DataSource) -> None:
    session.add(market(source))
    session.commit()
    with pytest.raises(IntegrityError):
        session.execute(delete(DataSource).where(DataSource.id == source.id))
    session.rollback()


def test_observation_requires_existing_source(session: Session, source: DataSource) -> None:
    rejected(session, market(source, source_id=uuid.uuid4()))


# ---- ingestion runs / raw / quality ---------------------------------------------------------


def run(source: DataSource, **overrides: Any) -> IngestionRun:
    base: dict[str, Any] = {"source_id": source.id, "started_at": T0}
    base.update(overrides)
    return IngestionRun(**base)


def test_run_cannot_end_before_it_starts(session: Session, source: DataSource) -> None:
    rejected(session, run(source, status="failed", ended_at=T0 - timedelta(seconds=1)))


def test_running_status_iff_open(session: Session, source: DataSource) -> None:
    rejected(session, run(source, status="running", ended_at=T0))
    rejected(session, run(source, status="succeeded", ended_at=None))


def test_run_status_and_counts_validated(session: Session, source: DataSource) -> None:
    rejected(session, run(source, status="weird", ended_at=T0))
    rejected(session, run(source, status="failed", ended_at=T0, rows_inserted=-1))


def test_raw_object_checksum_must_be_sha256_hex(session: Session, source: DataSource) -> None:
    r = run(source)
    session.add(r)
    session.commit()

    def raw(sha: str) -> RawObject:
        return RawObject(
            run_id=r.id,
            source_id=source.id,
            endpoint="https://example.test/q",
            fetched_at=T0,
            checksum_sha256=sha,
            storage_uri="file:///tmp/x",
        )

    rejected(session, raw("xyz"))
    rejected(session, raw("A" * 64))  # uppercase not canonical
    session.add(raw(SHA))
    session.commit()


def test_quality_event_severity_validated(session: Session, source: DataSource) -> None:
    r = run(source)
    session.add(r)
    session.commit()
    rejected(session, DataQualityEvent(run_id=r.id, rule="r", severity="meh"))
    rejected(session, DataQualityEvent(run_id=r.id, rule="r", severity="error", affected_count=-1))
    session.add(DataQualityEvent(run_id=r.id, rule="r", severity="error", context={"n": 1}))
    session.commit()


# ---- macro ---------------------------------------------------------------------------------


@pytest.fixture
def series(session: Session, source: DataSource) -> MacroSeries:
    s = MacroSeries(series_id="SYN1", source_id=source.id, units="percent")
    session.add(s)
    session.commit()
    return s


def macro(series: MacroSeries, **overrides: Any) -> MacroObservation:
    base: dict[str, Any] = {
        "series_id": series.series_id,
        "metadata_version": series.metadata_version,
        "observation_date": date(2026, 1, 5),
        "value": Decimal("-0.25"),
        "revision_key": "r1",
        "availability_basis": "first_seen",
        "available_at": T0,
    }
    base.update(overrides)
    return MacroObservation(**base)


def test_macro_allows_negative_and_null_values(session: Session, series: MacroSeries) -> None:
    session.add_all([macro(series), macro(series, observation_date=date(2026, 1, 6), value=None)])
    session.commit()


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "-Infinity"])
def test_macro_rejects_non_finite(session: Session, series: MacroSeries, bad: str) -> None:
    rejected(session, macro(series, value=Decimal(bad)))


def test_macro_duplicate_key_rejected_new_revision_ok(
    session: Session, series: MacroSeries
) -> None:
    session.add(macro(series))
    session.commit()
    rejected(session, macro(series, value=Decimal("1")))
    session.add(macro(series, revision_key="r2", value=Decimal("1")))
    session.commit()


def test_macro_requires_known_series_metadata_version(
    session: Session, series: MacroSeries
) -> None:
    rejected(session, macro(series, metadata_version=99))


def test_series_metadata_is_versioned(session: Session, source: DataSource) -> None:
    session.add_all(
        [
            MacroSeries(series_id="SYN2", metadata_version=1, source_id=source.id),
            MacroSeries(series_id="SYN2", metadata_version=2, source_id=source.id),
        ]
    )
    session.commit()
    rejected(session, MacroSeries(series_id="SYN2", metadata_version=2, source_id=source.id))


def test_driver_errors_do_not_leave_session_unusable(session: Session, source: DataSource) -> None:
    with pytest.raises((IntegrityError, DBAPIError)):
        session.execute(text("INSERT INTO market_observations (asset_id) VALUES ('x')"))
    session.rollback()
    assert session.execute(text("SELECT 1")).scalar_one() == 1
