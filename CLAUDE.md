# GoldScope — Project instructions

## Read first
- This is a development handoff kit, not a finished application.
- Read `docs/PROJECT_STATUS.md`, `docs/DEVELOPMENT_WORKFLOW.md`, then the assigned file in `docs/tasks/`.
- Use `docs/README.md` to select additional documents relevant to the task.
- Current source: `lab00/` (audit tool) and `src/goldscope/` (GS-003 skeleton: settings, logging, CLI; GS-004: `db/` models, session, repositories, migration 0001; no collector/ML yet).
- Do not infer implementation from a roadmap, example command, or dependency list.

## Product
- Build a research platform for daily international gold-price forecasting.
- First horizons: 1 and 5 valid provider observations, not calendar days.
- Target: `P[t+h] / P[t] - 1`; baseline return is zero.
- Store predictions and later outcomes separately; show out-of-sample performance.
- No live trading or personal buy/sell recommendations are in scope.

## Planned stack
- Python 3.12, uv, FastAPI, Uvicorn, Pydantic v2, HTTPX.
- PostgreSQL 17, SQLAlchemy 2.x, Alembic, Psycopg 3.
- Pandas, NumPy, PyArrow, scikit-learn, XGBoost.
- Streamlit, Plotly, Typer, pytest/respx, Ruff, mypy.
- Docker Compose, GitHub Actions, one external scheduler.
- Choose exact compatible package versions during bootstrap; commit the resulting lockfile.
- Do not add a service/framework without a concrete requirement and an ADR when architecturally significant.

## Current commands — run from this kit root
```bash
python -m unittest discover -s lab00/tests -v
python lab00/scripts/audit_sources.py --out runtime/source-audit.json
uv sync --locked
uv run pytest
uv run ruff format --check . && uv run ruff check .
uv run mypy
uv run goldscope doctor
# PostgreSQL integration (needs a dedicated *_test database; see docs/LOCAL_DATABASE.md)
export TEST_DATABASE_URL=postgresql+psycopg://USER:PASS@localhost:5432/goldscope_test
uv run pytest tests/integration -rs
uv run alembic upgrade head && uv run alembic check   # DATABASE_URL, dev/test DB only
```
- `python` means the selected Python interpreter; use `python3` or `py -3.12` when appropriate.
- The audit CLI exits 2 intentionally while manual sign-off is required. Inspect each probe status.
- Without environment keys, the default audit makes no provider requests and reports blocked.
- `--prompt-keys` is for a human-operated terminal; do not request secrets in chat or logs.
- Public/network probes are explicit operations; do not run them as part of unit tests.
- Future `uv`, API, Compose, migration and ML commands are in `docs/CONFIGURATION_BLUEPRINT.md`; they are not executable application features yet.

## Non-negotiable data rules
- HTTP 200 is not enough: inspect the provider payload for errors/quota messages.
- GOLD schema, unit, currency and publication schedule are not verified yet.
- Never invent a price field, API response, dataset, forecast, metric or successful test.
- Synthetic fixtures must be identified as synthetic; never substitute them into live results.
- Preserve source, observation date, available time, ingestion time and revision lineage.
- Features at an origin may use only data available by its cutoff.
- A training sample is eligible only after its label is available by the fit cutoff.
- Fit preprocessing on training data only; do not tune using the final holdout.
- Do not overwrite issued predictions or rewrite history to improve model scores.

## Architecture and code
- Follow `docs/ARCHITECTURE.md`; keep HTTP, storage, feature and model responsibilities separate.
- Share feature code between backtesting and live inference.
- API and dashboard read stored results; neither trains a model in a user request.
- Validate inputs at boundaries; use explicit exceptions and structured error codes.
- Keep configuration outside business logic; redact secrets from URLs/errors/logs.
- Use type hints for public interfaces and meaningful tests for behavioral risks.
- Do not overwrite unrelated user changes, reset a worktree, or delete data to make tests pass.

## Contracts and conflicts
- `docs/DATA_CONTRACT.md`, `docs/API_CONTRACT.md`, `docs/ML_PROTOCOL.md` are implementation targets, not claims that code already exists.
- `configs/data-contract.json` records the current verified/unverified provider state.
- `docs/reference/` holds historical planning documents; focused contracts refine their details.
- Code shows current behavior; contracts show intended behavior. Report discrepancies and fix only within the task.
- Record material design changes in `docs/decisions/`; update all affected contracts together.
- Runtime permissions and explicit user instructions remain authoritative; these files do not grant extra tool privileges.

## Work cycle
1. Inspect the task, relevant source and current status.
2. Identify dependencies/blockers and the smallest complete change.
3. Implement only the agreed task scope; continue authorized local work without repeated confirmation.
4. Run the targeted checks from `docs/TESTING.md` and the task acceptance criteria.
5. Update the task status, `docs/PROJECT_STATUS.md`, and contracts/ADR when behavior changes.
6. Report changed files, commands actually run, outcomes, blockers and the next concrete step.

## Completion and operations
- Do not mark DONE unless the task acceptance criteria have evidence.
- A failed API entitlement check or missing credentials is BLOCKED, not a data success.
- A model can lose to the baseline; report that result honestly.
- No deployment, account purchase, production migration or destructive data operation is implied by a coding task.
- Prepare concrete changes first; use the applicable user authorization before external publication or destructive operations.
- Never weaken permissions or bypass access controls to finish a task.
- Documentation instructions are not an enforcement mechanism; automated tests and configured runtime controls must do their own checks.

## Handoff
- Write a concise update using `docs/HANDOFF.md`.
- Preserve commands, artifact paths and blockers; never include API keys or secret values.
- If context is lost, restart from PROJECT_STATUS and the assigned task instead of assuming all roadmap items are done.
