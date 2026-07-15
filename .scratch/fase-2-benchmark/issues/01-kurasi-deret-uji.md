# Curate small real test benchmark (series only)

Status: ready-for-agent
Difficulty: medium
Depends: — (may consume F4-01 inventory if it exists)

## Spec

Hand-curate **15–30 real** time series from **1–2 mature** Indonesian public domains (recommended: Kemenkes
disease/DBD weekly + PIHPS food prices), as `Series` JSONL matching `src/gearts/schema.py`.

This is the **test** benchmark for RQ1/RQ2, so it must be real (field generalization) and **test-only**:
these sources must **not** reappear in the future train set (anti-leakage, brief §9.4). Record provenance
(source URL + retrieval date) per series.

- Series + minimal context/question **stub** only — no reasoning yet (that is F2-02).
- Cover varied difficulty: some clear-trend series, some ambiguous / with distractors.
- Span the four task types in the question stubs: anomaly/outbreak, trend characterization, segment
  comparison, explanation.

## Constraints

- Public data only; respect source ToS; no personal data.
- Every row must pass `Series` construction.

## Acceptance

- ≥ 15 real series, each valid `Series`.
- Provenance (source + date) recorded per series.
- Data under `data/` (gitignored), plus a small **committed** manifest listing source, date, task type,
  difficulty per series.
- No overlap with any planned train source.

## Comments
