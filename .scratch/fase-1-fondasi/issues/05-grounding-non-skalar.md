# Non-scalar grounding (deteksi_anomali index-set)

Status: ready-for-agent
Difficulty: medium
Depends: —

> Unblocked 2026-07-15: F1-01 decided (ADR-0003, Accepted). Target: exact set equality at synthesis-cleaning
> time, Jaccard similarity at eval time (threshold τ — pick a starting value, e.g. 0.8, and note it's tunable).

## Problem

`verify_sample` currently marks non-scalar steps `grounded=None` and excludes them from the score
(`verifier.py:110`). `deteksi_anomali` returns a **list of indices**, so it never counts — yet it is the
operation at the heart of the outbreak example. Brief v2 §4.4 ("kritik 2c") wants set-valued steps scored so
anomaly detection enters the main metric.

Grade a set-valued step by comparing the recomputed index set against the claimed set: exact match, or
Jaccard similarity ≥ a threshold.

## Spec

- Extend `verify_sample` to handle set-valued results with a set-grounding rule (exact or Jaccard ≥ τ).
- Keep the scalar path unchanged; parameterize τ.
- Include set-valued steps in `grounding_score`.

## Acceptance

- `deteksi_anomali` steps get a boolean `grounded` (not `None`).
- Tests lock: correct index set → grounded; wrong set → not grounded.
- `grounding_score` includes these steps; `pytest` green.

## Comments
