---
paths:
  - "tests/**"
  - "lab00/tests/**"
  - ".github/workflows/**"
---
# Testing rules
- Follow docs/TESTING.md and the task acceptance criteria.
- Unit/temporal tests are offline; use labeled fixtures and HTTP mocks.
- DB integration uses a dedicated PostgreSQL test database, never production fallback.
- Test meaningful failure behavior, temporal leakage and idempotency.
- Do not assert that a market model must beat baseline.
- Record actual commands, environment, exit codes and results.
- Never mark an unrun test as passed; distinguish expected audit exit 2 from test results.
