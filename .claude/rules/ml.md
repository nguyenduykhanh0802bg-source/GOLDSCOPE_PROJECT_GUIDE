---
paths:
  - "src/goldscope/ml/**"
  - "src/goldscope/features/**"
  - "tests/temporal/**"
  - "notebooks/**"
---
# ML rules
- Read docs/ML_PROTOCOL.md before changing features, targets or evaluation.
- h=1/5 counts valid provider observations, not calendar days.
- Share feature code between training and inference.
- Fit transforms only on training windows; labels must mature by fit cutoff.
- Never tune on final holdout or relabel in-sample forecasts as out-of-sample.
- Always compare the same origins/horizon against a zero-return baseline.
- Store per-origin predictions, protocol/config/schema/data hashes and metrics.
- Model failure to beat baseline is a legitimate result; do not alter evidence.
- Interval coverage is empirical; do not invent forecast confidence or PnL.
