from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from goldscope.core.errors import DataConflictError
from goldscope.db.models import DataQualityEvent, IngestionRun, MacroSeries, MarketObservation
from goldscope.db.repositories import (
    AddResult,
    NewMacroObservation,
    NewMarketObservation,
    add_macro_observation,
    add_market_observation,
    add_quality_event,
    add_raw_object,
    finish_run,
    get_or_create_source,
    start_run,
)
from goldscope.db.session import session_scope

T0 = datetime(2026, 1, 5, 12, 0, tzinfo=UTC)
T1 = datetime(2026, 1, 5, 12, 1, tzinfo=UTC)


def obs(source_id: uuid.UUID, **kw: Any) -> NewMarketObservation:
    base: dict[str, Any] = {
        "asset_id": "TEST_ASSET",
        "source_id": source_id,
        "observation_date": date(2026, 1, 5),
        "price": Decimal("100.5"),
        "currency": "XXX",
        "unit": "test-unit",
        "price_definition": "synthetic",
        "revision_key": "r1",
        "availability_basis": "first_seen",
        "available_at": T0,
    }
    base.update(kw)
    return NewMarketObservation(**base)


def count(session: Session, model: type) -> int:
    return session.execute(select(func.count()).select_from(model)).scalar_one()


def test_get_or_create_source_is_idempotent_and_keeps_existing_policy(engine: Engine) -> None:
    with session_scope(engine) as s:
        a = get_or_create_source(s, provider="p", dataset_key="d", time_policy={"v": 1})
        b = get_or_create_source(s, provider="p", dataset_key="d", time_policy={"v": 2})
        assert a.id == b.id
        assert b.time_policy == {"v": 1}  # change policy => new policy_version, not an update
        c = get_or_create_source(s, provider="p", dataset_key="d", policy_version=2)
        assert c.id != a.id


def test_retry_same_payload_is_noop_and_new_revision_is_added(engine: Engine) -> None:
    with session_scope(engine) as s:
        src = get_or_create_source(s, provider="p", dataset_key="d")
        assert add_market_observation(s, obs(src.id)) is AddResult.INSERTED
        assert add_market_observation(s, obs(src.id)) is AddResult.DUPLICATE
        assert count(s, MarketObservation) == 1
        assert add_market_observation(s, obs(src.id, revision_key="r2", price=Decimal("101"))) is (
            AddResult.INSERTED
        )
        assert count(s, MarketObservation) == 2


def test_same_key_different_content_is_conflict_not_update(engine: Engine) -> None:
    with session_scope(engine) as s:
        src = get_or_create_source(s, provider="p", dataset_key="d")
        add_market_observation(s, obs(src.id))
        with pytest.raises(DataConflictError) as info:
            add_market_observation(s, obs(src.id, price=Decimal("999")))
        assert info.value.code == "data_conflict"
    with Session(engine) as s2:
        assert s2.execute(select(MarketObservation.price)).scalar_one() == Decimal("100.5")


def test_invalid_price_surfaces_as_integrity_error_and_adds_nothing(engine: Engine) -> None:
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError), session_scope(engine) as s:
        src = get_or_create_source(s, provider="p", dataset_key="d")
        add_market_observation(s, obs(src.id, price=Decimal("-5")))
    with Session(engine) as s2:
        assert count(s2, MarketObservation) == 0


def test_rollback_leaves_no_half_written_business_rows(engine: Engine) -> None:
    class Boom(Exception):
        pass

    with pytest.raises(Boom), session_scope(engine) as s:
        src = get_or_create_source(s, provider="p", dataset_key="d")
        run = start_run(s, source_id=src.id, started_at=T0)
        add_market_observation(s, obs(src.id))
        add_quality_event(s, run_id=run.id, rule="x", severity="info")
        raise Boom
    with Session(engine) as s2:
        assert count(s2, MarketObservation) == 0
        assert count(s2, IngestionRun) == 0
        assert count(s2, DataQualityEvent) == 0


def test_run_lifecycle_and_error_message_is_redacted(engine: Engine) -> None:
    with session_scope(engine) as s:
        src = get_or_create_source(s, provider="p", dataset_key="d")
        run = start_run(s, source_id=src.id, started_at=T0)
        assert run.status == "running" and run.ended_at is None
        finish_run(
            s,
            run,
            status="failed",
            ended_at=T1,
            error_code="provider_error",
            error_message="GET https://x.test/q?apikey=SUPERSECRET failed",
        )
        raw = add_raw_object(
            s,
            run_id=run.id,
            source_id=src.id,
            endpoint="https://x.test/q?apikey=SUPERSECRET&f=1",
            fetched_at=T0,
            checksum_sha256="b" * 64,
            storage_uri="file:///tmp/raw",
            is_error=True,
        )
        assert "SUPERSECRET" not in (run.error_message or "")
        assert "SUPERSECRET" not in raw.endpoint


def test_macro_repository_idempotency_null_and_conflict(engine: Engine) -> None:
    with session_scope(engine) as s:
        src = get_or_create_source(s, provider="p", dataset_key="m")
        s.add(MacroSeries(series_id="SYN1", source_id=src.id))
        s.flush()

        def m(**kw: Any) -> NewMacroObservation:
            base: dict[str, Any] = {
                "series_id": "SYN1",
                "metadata_version": 1,
                "observation_date": date(2026, 1, 5),
                "value": None,
                "revision_key": "r1",
                "availability_basis": "first_seen",
                "available_at": T0,
            }
            base.update(kw)
            return NewMacroObservation(**base)

        assert add_macro_observation(s, m()) is AddResult.INSERTED
        assert add_macro_observation(s, m()) is AddResult.DUPLICATE  # NULL == NULL by content
        with pytest.raises(DataConflictError):
            add_macro_observation(s, m(value=Decimal("1.5")))
        assert add_macro_observation(s, m(revision_key="r2", value=Decimal("-1.5"))) is (
            AddResult.INSERTED
        )
