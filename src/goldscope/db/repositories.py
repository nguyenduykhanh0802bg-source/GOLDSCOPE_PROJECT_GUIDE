"""Repositories. Idempotent writes rely on DB unique constraints, never on read-then-write.

Rule (docs/DATABASE_DESIGN.md): a retry with identical content is a no-op; the same business
key with different content is a conflict that needs a new revision_key - never an update.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from goldscope.core.errors import DataConflictError
from goldscope.core.logging import redact_text
from goldscope.db.models import (
    DataQualityEvent,
    DataSource,
    IngestionRun,
    MacroObservation,
    MarketObservation,
    RawObject,
)


class AddResult(StrEnum):
    INSERTED = "inserted"
    DUPLICATE = "duplicate"  # identical content already stored; nothing changed


def get_or_create_source(
    session: Session,
    *,
    provider: str,
    dataset_key: str,
    policy_version: int = 1,
    endpoint_key: str | None = None,
    time_policy: dict[str, Any] | None = None,
    unit_policy: dict[str, Any] | None = None,
    license_policy: dict[str, Any] | None = None,
) -> DataSource:
    """Existing rows are returned unchanged: a policy change must use a new policy_version."""
    session.execute(
        pg_insert(DataSource)
        .values(
            provider=provider,
            dataset_key=dataset_key,
            policy_version=policy_version,
            endpoint_key=endpoint_key,
            time_policy=time_policy or {},
            unit_policy=unit_policy or {},
            license_policy=license_policy or {},
        )
        .on_conflict_do_nothing(index_elements=["provider", "dataset_key", "policy_version"])
    )
    return session.execute(
        select(DataSource).where(
            DataSource.provider == provider,
            DataSource.dataset_key == dataset_key,
            DataSource.policy_version == policy_version,
        )
    ).scalar_one()


def start_run(session: Session, *, source_id: uuid.UUID, started_at: datetime) -> IngestionRun:
    run = IngestionRun(source_id=source_id, started_at=started_at, status="running")
    session.add(run)
    session.flush()
    return run


def finish_run(
    session: Session,
    run: IngestionRun,
    *,
    status: str,
    ended_at: datetime,
    rows_fetched: int = 0,
    rows_inserted: int = 0,
    rows_rejected: int = 0,
    error_code: str | None = None,
    error_message: str | None = None,
) -> IngestionRun:
    run.status = status
    run.ended_at = ended_at
    run.rows_fetched = rows_fetched
    run.rows_inserted = rows_inserted
    run.rows_rejected = rows_rejected
    run.error_code = error_code
    run.error_message = redact_text(error_message) if error_message else None
    session.flush()
    return run


def add_raw_object(
    session: Session,
    *,
    run_id: uuid.UUID,
    source_id: uuid.UUID,
    endpoint: str,
    fetched_at: datetime,
    checksum_sha256: str,
    storage_uri: str,
    http_status: int | None = None,
    content_type: str | None = None,
    schema_version: str | None = None,
    size_bytes: int | None = None,
    is_error: bool = False,
) -> RawObject:
    raw = RawObject(
        run_id=run_id,
        source_id=source_id,
        endpoint=redact_text(endpoint),
        fetched_at=fetched_at,
        checksum_sha256=checksum_sha256,
        storage_uri=storage_uri,
        http_status=http_status,
        content_type=content_type,
        schema_version=schema_version,
        size_bytes=size_bytes,
        is_error=is_error,
    )
    session.add(raw)
    session.flush()
    return raw


def add_quality_event(
    session: Session,
    *,
    run_id: uuid.UUID,
    rule: str,
    severity: str,
    affected_count: int = 0,
    context: dict[str, Any] | None = None,
) -> DataQualityEvent:
    event = DataQualityEvent(
        run_id=run_id,
        rule=rule,
        severity=severity,
        affected_count=affected_count,
        context=context or {},
    )
    session.add(event)
    session.flush()
    return event


@dataclass(frozen=True)
class NewMarketObservation:
    asset_id: str
    source_id: uuid.UUID
    observation_date: date
    price: Decimal
    currency: str
    unit: str
    price_definition: str
    revision_key: str
    availability_basis: str = "unknown"
    available_at: datetime | None = None
    source_published_at: datetime | None = None
    vintage_date: date | None = None
    raw_object_id: uuid.UUID | None = None
    ingested_at: datetime | None = None


def add_market_observation(session: Session, obs: NewMarketObservation) -> AddResult:
    values: dict[str, Any] = {
        "asset_id": obs.asset_id,
        "source_id": obs.source_id,
        "observation_date": obs.observation_date,
        "price": obs.price,
        "currency": obs.currency,
        "unit": obs.unit,
        "price_definition": obs.price_definition,
        "revision_key": obs.revision_key,
        "availability_basis": obs.availability_basis,
        "available_at": obs.available_at,
        "source_published_at": obs.source_published_at,
        "vintage_date": obs.vintage_date,
        "raw_object_id": obs.raw_object_id,
    }
    if obs.ingested_at is not None:
        values["ingested_at"] = obs.ingested_at
    key = ["asset_id", "source_id", "observation_date", "revision_key"]
    inserted = session.execute(
        pg_insert(MarketObservation)
        .values(**values)
        .on_conflict_do_nothing(index_elements=key)
        .returning(MarketObservation.id)
    ).scalar_one_or_none()
    if inserted is not None:
        return AddResult.INSERTED
    existing = session.execute(
        select(MarketObservation).where(
            MarketObservation.asset_id == obs.asset_id,
            MarketObservation.source_id == obs.source_id,
            MarketObservation.observation_date == obs.observation_date,
            MarketObservation.revision_key == obs.revision_key,
        )
    ).scalar_one()
    same = (
        existing.price == obs.price
        and existing.currency == obs.currency
        and existing.unit == obs.unit
        and existing.price_definition == obs.price_definition
    )
    if not same:
        raise DataConflictError(
            f"market observation {obs.asset_id} {obs.observation_date} already exists with "
            "different content under the same revision_key; use a new revision_key"
        )
    return AddResult.DUPLICATE


@dataclass(frozen=True)
class NewMacroObservation:
    series_id: str
    metadata_version: int
    observation_date: date
    value: Decimal | None
    revision_key: str
    availability_basis: str = "unknown"
    available_at: datetime | None = None
    source_published_at: datetime | None = None
    vintage_date: date | None = None
    raw_object_id: uuid.UUID | None = None


def add_macro_observation(session: Session, obs: NewMacroObservation) -> AddResult:
    key = ["series_id", "observation_date", "revision_key"]
    inserted = session.execute(
        pg_insert(MacroObservation)
        .values(
            series_id=obs.series_id,
            metadata_version=obs.metadata_version,
            observation_date=obs.observation_date,
            value=obs.value,
            revision_key=obs.revision_key,
            availability_basis=obs.availability_basis,
            available_at=obs.available_at,
            source_published_at=obs.source_published_at,
            vintage_date=obs.vintage_date,
            raw_object_id=obs.raw_object_id,
        )
        .on_conflict_do_nothing(index_elements=key)
        .returning(MacroObservation.id)
    ).scalar_one_or_none()
    if inserted is not None:
        return AddResult.INSERTED
    existing = session.execute(
        select(MacroObservation).where(
            MacroObservation.series_id == obs.series_id,
            MacroObservation.observation_date == obs.observation_date,
            MacroObservation.revision_key == obs.revision_key,
        )
    ).scalar_one()
    if existing.value != obs.value:
        raise DataConflictError(
            f"macro observation {obs.series_id} {obs.observation_date} already exists with a "
            "different value under the same revision_key; use a new revision_key"
        )
    return AddResult.DUPLICATE
