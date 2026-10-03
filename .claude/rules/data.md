---
paths:
  - "src/goldscope/collectors/**"
  - "src/goldscope/data/**"
  - "src/goldscope/features/**"
  - "configs/**"
  - "lab00/scripts/**"
---
# Data rules
- Read docs/DATA_CONTRACT.md and the assigned task.
- GOLD provider mapping is unverified until source audit supplies evidence.
- Do not turn HTTP 200 provider errors into rows.
- Preserve raw/revision/time provenance and idempotent business keys.
- Use available_at, not observation_date alone, for feature eligibility.
- Never backward-fill from future data or invent missing prices.
- Keep synthetic fixtures separate from verified provider samples.
- Do not log keys, full authenticated URLs or secrets in exceptions.
- Changing provider/time/calendar policy requires a versioned contract update.
