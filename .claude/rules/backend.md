---
paths:
  - "src/goldscope/api/**"
  - "src/goldscope/services/**"
  - "src/goldscope/db/**"
  - "migrations/**"
  - "dashboard/**"
---
# Backend and presentation rules
- Read docs/ARCHITECTURE.md, docs/API_CONTRACT.md and docs/DATABASE_DESIGN.md as relevant.
- Keep routers thin; do not train or fetch market providers on a dashboard GET.
- Dashboard calls API and does not access DB/provider credentials directly.
- Preserve response units, modes, timestamps, nulls and stale states.
- Issued predictions are immutable; outcomes have separate revisions.
- Use DB constraints/transactions for deduplication and model promotion.
- Add migration revisions for shared applied schema; do not rewrite migration history.
- Do not add public management endpoints without an authorization design.
