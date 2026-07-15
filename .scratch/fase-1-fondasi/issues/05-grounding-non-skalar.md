# Non-scalar grounding (deteksi_anomali index-set)

Status: needs-info
Difficulty: medium
Depends: F1-01

## Problem

`verify_sample` currently marks non-scalar steps `grounded=None` and excludes them from the score
(`verifier.py:110`). `deteksi_anomali` returns a **list of indices**, so it never counts — yet it is the
operation at the heart of the outbreak example. Brief v2 §4.4 ("kritik 2c") wants set-valued steps scored so
anomaly detection enters the main metric.

Grade a set-valued step by comparing the recomputed index set against the claimed set: exact match, or
Jaccard similarity ≥ a threshold.

## Blocked by

**F1-01** must first finalize `deteksi_anomali` semantics (population window, one- vs two-sided, and what its
`hasil` holds in a JSONL step) and the grounding rule for sets. Until then this cannot be implemented
correctly — the label contract is undecided.

## Spec (once unblocked)

- Extend `verify_sample` to handle set-valued results with a set-grounding rule (exact or Jaccard ≥ τ).
- Keep the scalar path unchanged; parameterize τ.
- Include set-valued steps in `grounding_score`.

## Acceptance

- `deteksi_anomali` steps get a boolean `grounded` (not `None`).
- Tests lock: correct index set → grounded; wrong set → not grounded.
- `grounding_score` includes these steps; `pytest` green.

## Comments
