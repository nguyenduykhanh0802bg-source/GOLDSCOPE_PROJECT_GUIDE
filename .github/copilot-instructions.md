# GoldScope — AI Coding Instructions

This is a **research platform for daily gold-price forecasting** with strict data governance and a modular architecture. Read [CLAUDE.md](../CLAUDE.md) and [docs/PROJECT_STATUS.md](../docs/PROJECT_STATUS.md) before starting any task.

## Architecture Essentials

**Monolith with clear module boundaries** ([docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)):

- **`src/goldscope/core/`** — Settings (Pydantic), logging (JSON/redact), errors, time policy. No hardcoded secrets.
- **`src/goldscope/db/`** — SQLAlchemy 2.x models (UUID PKs, NUMERIC prices unscaled), repositories (idempotent upserts via PG constraints), `session_scope` context manager (commit/rollback).
- **`src/goldscope/cli.py`** — Typer commands; business logic lives in services, not CLI.
- **Future modules:** `collectors/`, `features/`, `ml/`, `services/`, `api/`, `jobs/`, `dashboard/` — each owns a slice; no circular imports.

**Data flows:**
- **Ingest:** lock → HTTP → raw/checksum storage → normalize/validate → transaction write observations + revisions + quality summary.
- **Research:** snapshot → features + targets → train/validate windows → predictions/metrics → manifest.
- **Live forecast:** pick model → fetch input by cutoff → feature schema validation → predict + store with business-key dedup.

**Key principle:** Retry with identical content is a no-op (DB unique constraints enforce this); retry with different content is a conflict (needs new `revision_key`). Never "SELECT then INSERT" — always use `pg_insert(...).on_conflict_do_nothing()`.

## Development Workflow

1. **Before coding:** Read task spec, `PROJECT_STATUS.md`, relevant contract (`DATA_CONTRACT.md`, `API_CONTRACT.md`, `ML_PROTOCOL.md`), and actual source code — not roadmaps.
2. **During:** Separate logic from IO for testability. Include validation, failure paths, and logging. Synthetic fixtures are labeled; don't invent API responses.
3. **Data rules (non-negotiable):**
   - HTTP 200 ≠ success — inspect payload for errors/quota.
   - Preserve source, observation date, ingestion time, and lineage.
   - Features at cutoff D use only data available by D; labels eligible only after label cutoff.
   - Never rewrite history or overwrite issued predictions.
4. **Testing:** Unit tests run offline (network blocked); integration tests reach PostgreSQL only. Mark integration tests with `@pytest.mark.integration`. Use respx for HTTP mocking.
5. **Handoff:** Update task status with changed files, commands run, evidence, and blockers. Report discrepancies between docs and code. Merge changes into contracts/ADRs if behavior changes.

## Commands & Setup

Run from repo root (environment requires **Python 3.12+**, **uv**, **PostgreSQL 17**):

```bash
# Environment
uv sync --locked

# Tests (unit only by default; integration requires TEST_DATABASE_URL)
uv run pytest
TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/goldscope_test uv run pytest tests/integration -rs

# Linting & type checking
uv run ruff format --check . && uv run ruff check .
uv run mypy

# CLI doctor command
uv run goldscope doctor

# Migrations (dev/test DB only; never on production schema)
uv run alembic upgrade head && uv run alembic check

# Legacy audit tool (Lab 00)
python lab00/scripts/audit_sources.py --out runtime/source-audit.json
```

**Note:** `audit_sources.py` exits code 2 intentionally (manual sign-off required); code 3 means not-implemented placeholder in CLI. Exit 0/non-zero from pytest; don't mix them.

## Contracts & Decisions

- **Contracts** (`docs/DATA_CONTRACT.md`, `API_CONTRACT.md`, `ML_PROTOCOL.md`) define *intended* behavior; code shows *actual* behavior. Report mismatches; fix only within task scope.
- **ADR files** (`docs/decisions/`) record architecture choices (e.g., ADR-0006: UUID PKs, NUMERIC unscaled, no cascading deletes). **New ADRs required for:** tearing down services, changing provider/asset/horizon, adding LLM/queue/broker, database migration, breaking API changes, retrain policy changes.
- **Migrations** in `migrations/versions/` are append-only; never edit applied migrations. New deployments use `alembic upgrade head`.

## Patterns & Conventions

| Pattern | Example | Rule |
|---------|---------|------|
| **Settings load** | `load_settings()` in `core/settings.py` | No implicit `.env` read; pass `env_file=` explicitly. All values optional at load time (tests/docs work offline). Call `require_secret(key)` only when feature needs it. |
| **DB writes** | `repositories.py` / `pg_insert(...).on_conflict_do_nothing(...)` | Idempotent upsert via PK/unique constraints, never app-level retry logic. Use `session_scope(engine)` for auto-rollback. |
| **Logging** | `configure_logging()` with `JsonFormatter` | Redact secrets with `redact_text()`. Use run_id/request_id. Never log URLs with API keys. |
| **Feature cutoffs** | Validation in features module | Features at snapshot D must use only data available *before* D. Training label must be available by its label cutoff, not guessed/backfilled. |
| **Error handling** | `raise ConfigError(...)`, `DataConflictError(...)` | Explicit exception types at boundaries. Never swallow or invent errors; error codes go in API schema. |
| **Test fixtures** | `tests/fixtures/` or `conftest.py` | Synthetic data is labeled as synthetic. Never substitute synthetic into live results or CI without disclosure. |

## Common Blockers

- **GS-001/002 blocked:** No authenticated GOLD provider response yet. Don't invent GOLD schema; wait for audit verification before collector/model code.
- **Live network requests:** Never run in unit tests. Unit tests have network blocked at socket level (`conftest.py`). Use `respx` for HTTP mocking.
- **Database:** Integration tests need `TEST_DATABASE_URL` env var pointing to a dedicated test database (not dev, not production). Schema is managed by `alembic`, not `create_all()`.
- **Model versioning:** Features at inference must match training schema (hash checked in manifest). Don't silently drop/reorder features.
- **Secrets in output:** Always use `SecretStr` from Pydantic, check logs/exceptions for leaked URLs, never echo credentials in chat/terminal.

## Questions Before Coding

- Is the task scope limited to a single module, or does it cross `core/`, `db/`, `api/`, `ml/` boundaries?
- Are there any breaking contract changes? If yes, ADR + update docs in same PR.
- Does the feature touch data ingestion, feature timing, or model training? Verify cutoff/label maturity rules apply.
- Do you need PostgreSQL or can this test offline? (Check task acceptance criteria.)
