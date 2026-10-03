"""baseline ingestion and observations

GS-004: data_sources, ingestion_runs, raw_objects, market_observations, macro_series,
macro_observations, data_quality_events. Reviewed by hand after autogenerate.

Revision ID: 0001
Revises: (none, baseline)
Create Date: 2026-10-01 01:22:44.903905
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("dataset_key", sa.String(), nullable=False),
        sa.Column("policy_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("endpoint_key", sa.String(), nullable=True),
        sa.Column("mapping_status", sa.String(), server_default="unverified", nullable=False),
        sa.Column(
            "time_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "unit_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "license_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "mapping_status IN ('unverified', 'verified', 'deprecated')",
            name=op.f("ck_data_sources_mapping_status_valid"),
        ),
        sa.CheckConstraint(
            "provider <> '' AND dataset_key <> ''", name=op.f("ck_data_sources_keys_not_empty")
        ),
        sa.CheckConstraint(
            "policy_version >= 1", name=op.f("ck_data_sources_policy_version_positive")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_sources")),
        sa.UniqueConstraint(
            "provider",
            "dataset_key",
            "policy_version",
            name=op.f("uq_data_sources_provider_dataset_policy"),
        ),
    )
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("started_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("ended_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("status", sa.String(), server_default="running", nullable=False),
        sa.Column("rows_fetched", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rows_inserted", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rows_rejected", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(status = 'running') = (ended_at IS NULL)",
            name=op.f("ck_ingestion_runs_running_iff_open"),
        ),
        sa.CheckConstraint(
            "status IN ('running', 'succeeded', 'failed', 'partial', 'skipped')",
            name=op.f("ck_ingestion_runs_status_valid"),
        ),
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name=op.f("ck_ingestion_runs_ended_after_started"),
        ),
        sa.CheckConstraint(
            "rows_fetched >= 0 AND rows_inserted >= 0 AND rows_rejected >= 0",
            name=op.f("ck_ingestion_runs_counts_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["data_sources.id"],
            name=op.f("fk_ingestion_runs_source_id_data_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_runs")),
    )
    op.create_index(
        "ix_ingestion_runs_source_started",
        "ingestion_runs",
        ["source_id", "started_at"],
        unique=False,
    )
    op.create_table(
        "macro_series",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("series_id", sa.String(), nullable=False),
        sa.Column("metadata_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("units", sa.String(), nullable=True),
        sa.Column("frequency", sa.String(), nullable=True),
        sa.Column(
            "release_schedule",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("series_id <> ''", name=op.f("ck_macro_series_series_not_empty")),
        sa.CheckConstraint(
            "metadata_version >= 1", name=op.f("ck_macro_series_metadata_version_positive")
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["data_sources.id"], name=op.f("fk_macro_series_source_id_data_sources")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_macro_series")),
        sa.UniqueConstraint(
            "series_id", "metadata_version", name=op.f("uq_macro_series_series_metadata_version")
        ),
    )
    op.create_table(
        "data_quality_events",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("rule", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("affected_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "context",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("rule <> ''", name=op.f("ck_data_quality_events_rule_not_empty")),
        sa.CheckConstraint(
            "severity IN ('info', 'warning', 'error', 'critical')",
            name=op.f("ck_data_quality_events_severity_valid"),
        ),
        sa.CheckConstraint(
            "affected_count >= 0", name=op.f("ck_data_quality_events_affected_count_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["ingestion_runs.id"],
            name=op.f("fk_data_quality_events_run_id_ingestion_runs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_quality_events")),
    )
    op.create_index(
        "ix_data_quality_events_created_at", "data_quality_events", ["created_at"], unique=False
    )
    op.create_index(
        "ix_data_quality_events_run_id", "data_quality_events", ["run_id"], unique=False
    )
    op.create_table(
        "raw_objects",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("fetched_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(), nullable=True),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("is_error", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.CheckConstraint(
            "checksum_sha256 ~ '^[0-9a-f]{64}$'", name=op.f("ck_raw_objects_checksum_sha256_hex")
        ),
        sa.CheckConstraint(
            "size_bytes IS NULL OR size_bytes >= 0", name=op.f("ck_raw_objects_size_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["ingestion_runs.id"], name=op.f("fk_raw_objects_run_id_ingestion_runs")
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["data_sources.id"], name=op.f("fk_raw_objects_source_id_data_sources")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_raw_objects")),
    )
    op.create_index(
        "ix_raw_objects_checksum_sha256", "raw_objects", ["checksum_sha256"], unique=False
    )
    op.create_index("ix_raw_objects_run_id", "raw_objects", ["run_id"], unique=False)
    op.create_table(
        "macro_observations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("series_id", sa.String(), nullable=False),
        sa.Column("metadata_version", sa.Integer(), nullable=False),
        sa.Column("observation_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(), nullable=True),
        sa.Column("revision_key", sa.String(), nullable=False),
        sa.Column("raw_object_id", sa.UUID(), nullable=True),
        sa.Column("source_published_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("available_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "ingested_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("vintage_date", sa.Date(), nullable=True),
        sa.Column("availability_basis", sa.String(), server_default="unknown", nullable=False),
        sa.CheckConstraint(
            "availability_basis = 'unknown' OR available_at IS NOT NULL",
            name=op.f("ck_macro_observations_available_at_required"),
        ),
        sa.CheckConstraint(
            "availability_basis IN ('verified', 'conservative_proxy', 'first_seen', 'unknown')",
            name=op.f("ck_macro_observations_availability_valid"),
        ),
        sa.CheckConstraint(
            "revision_key <> ''", name=op.f("ck_macro_observations_revision_key_not_empty")
        ),
        sa.CheckConstraint(
            "value IS NULL OR (value <> 'NaN' AND value <> 'Infinity' AND value <> '-Infinity')",
            name=op.f("ck_macro_observations_value_finite_or_null"),
        ),
        sa.ForeignKeyConstraint(
            ["raw_object_id"],
            ["raw_objects.id"],
            name=op.f("fk_macro_observations_raw_object_id_raw_objects"),
        ),
        sa.ForeignKeyConstraint(
            ["series_id", "metadata_version"],
            ["macro_series.series_id", "macro_series.metadata_version"],
            name="fk_macro_observations_series_macro_series",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_macro_observations")),
        sa.UniqueConstraint(
            "series_id",
            "observation_date",
            "revision_key",
            name=op.f("uq_macro_observations_business_key"),
        ),
    )
    op.create_index(
        "ix_macro_obs_series_available_at",
        "macro_observations",
        ["series_id", "available_at"],
        unique=False,
    )
    op.create_index(
        "ix_macro_obs_series_date",
        "macro_observations",
        ["series_id", "observation_date"],
        unique=False,
    )
    op.create_table(
        "market_observations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("observation_date", sa.Date(), nullable=False),
        sa.Column("price", sa.Numeric(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("price_definition", sa.String(), nullable=False),
        sa.Column("revision_key", sa.String(), nullable=False),
        sa.Column("raw_object_id", sa.UUID(), nullable=True),
        sa.Column("source_published_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("available_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "ingested_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("vintage_date", sa.Date(), nullable=True),
        sa.Column("availability_basis", sa.String(), server_default="unknown", nullable=False),
        sa.CheckConstraint("asset_id <> ''", name=op.f("ck_market_observations_asset_not_empty")),
        sa.CheckConstraint(
            "availability_basis = 'unknown' OR available_at IS NOT NULL",
            name=op.f("ck_market_observations_available_at_required"),
        ),
        sa.CheckConstraint(
            "availability_basis IN ('verified', 'conservative_proxy', 'first_seen', 'unknown')",
            name=op.f("ck_market_observations_availability_valid"),
        ),
        sa.CheckConstraint(
            "price > 0 AND price <> 'NaN' AND price <> 'Infinity' AND price <> '-Infinity'",
            name=op.f("ck_market_observations_price_positive_finite"),
        ),
        sa.CheckConstraint(
            "revision_key <> ''", name=op.f("ck_market_observations_revision_key_not_empty")
        ),
        sa.ForeignKeyConstraint(
            ["raw_object_id"],
            ["raw_objects.id"],
            name=op.f("fk_market_observations_raw_object_id_raw_objects"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["data_sources.id"],
            name=op.f("fk_market_observations_source_id_data_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_market_observations")),
        sa.UniqueConstraint(
            "asset_id",
            "source_id",
            "observation_date",
            "revision_key",
            name=op.f("uq_market_observations_business_key"),
        ),
    )
    op.create_index(
        "ix_market_obs_asset_source_date",
        "market_observations",
        ["asset_id", "source_id", "observation_date"],
        unique=False,
    )
    op.create_index(
        "ix_market_obs_available_at", "market_observations", ["available_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_market_obs_available_at", table_name="market_observations")
    op.drop_index("ix_market_obs_asset_source_date", table_name="market_observations")
    op.drop_table("market_observations")
    op.drop_index("ix_macro_obs_series_date", table_name="macro_observations")
    op.drop_index("ix_macro_obs_series_available_at", table_name="macro_observations")
    op.drop_table("macro_observations")
    op.drop_index("ix_raw_objects_run_id", table_name="raw_objects")
    op.drop_index("ix_raw_objects_checksum_sha256", table_name="raw_objects")
    op.drop_table("raw_objects")
    op.drop_index("ix_data_quality_events_run_id", table_name="data_quality_events")
    op.drop_index("ix_data_quality_events_created_at", table_name="data_quality_events")
    op.drop_table("data_quality_events")
    op.drop_table("macro_series")
    op.drop_index("ix_ingestion_runs_source_started", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_table("data_sources")
