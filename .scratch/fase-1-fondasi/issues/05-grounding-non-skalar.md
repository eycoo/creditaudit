# Non-scalar grounding (deteksi_anomali index-set)

Status: done
Difficulty: medium
Depends: —

> Session A (track-a, 2026-07-15): TDD. Set-grounding in verify_sample via Jaccard(recomputed, claimed) ≥ τ;
> τ default 1.0 = exact set equality (clean-time), τ<1 for eval. Set steps enter grounding_score. builder.

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

- **Done 2026-07-15 (track-a, TDD).** Extended `verify_sample` with a set-grounding path: results that are
  list/tuple/set/ndarray (i.e. `deteksi_anomali` index lists) now ground when
  `Jaccard(recomputed_set, claimed_set) ≥ jaccard_tau`. Added `jaccard_tau` param, **default 1.0 = exact set
  equality** (dataset-cleaning setting per ADR-0003 Item 1); pass a lower τ (e.g. 0.8) at eval time.
  Both-empty → Jaccard 1.0 (claiming no anomalies where there are none grounds). Set steps now enter
  `grounding_score` (renamed the internal counter `scalar_count`→`scored_count`); the truly-unhandled
  non-scalar branch (`grounded=None`) is kept as defensive fallback for any future non-set non-scalar op.
  Set-valued results are **not** bound as `langkah{N}` (ADR-0003 Item 4 — only scalars are bindable).
- **Tests** (`tests/test_verifier.py`): correct set → grounded + 100%; wrong set → not grounded + 0%;
  Jaccard τ threshold ({4} vs {4,5}=0.5: fails at τ=1.0, grounds at τ=0.5); empty-set grounds; mixed
  scalar+set both counted (50% when only the set step breaks). Hand-checked fixture series `[1,1,1,1,10]`
  (`deteksi_anomali(z=1.5)` → `{4}`). Full suite **51 passed**.
- No lab-notebook entry — this is a code feature, not an experiment. ADR-0003 already records the decision.
