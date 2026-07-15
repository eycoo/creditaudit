# Lock finalized operation semantics in code + tests

Status: ready-for-agent
Difficulty: medium
Depends: —

## Problem

ADR-0003 (Accepted, 2026-07-15) finalized the five provisional operation semantics. `operations.py` still
carries the old provisional `# ponytail` markers and no tests lock the finalized rules. `CONTEXT.md` is
already updated (source of truth for the target semantics — read it first).

## Spec

In `src/gearts/operations.py`:
- Remove the two `# ponytail` markers (`deteksi_anomali`, `bandingkan_segmen`) and replace with short
  docstrings pinning the finalized semantics (see `CONTEXT.md` operation table / ADR-0003).
- `z_score` / `deteksi_anomali`: confirm `ddof=0` (population std) on both — already implemented, add a
  one-line comment noting it's deliberate (not sample std) and that the two must agree numerically.
- `bandingkan_segmen`: docstring pinning `mean(r2) − mean(r1)`, scalar, absolute difference only (no
  percent/ratio mode) — already implemented, no behavior change.
- No behavior change is expected from this issue for the scalar ops — this is docstring + test lock, not a
  semantics change. `deteksi_anomali`'s grounding (non-scalar scoring) is **out of scope** — that's F1-05.

In `tests/test_operations.py` (or `tests/test_verifier.py` where relevant), add tests locking:
- `z_score` with an explicit baseline-window population argument (e.g. `z_score(nilai[15], nilai[0:8])`)
  differs from the whole-series default on a trending series.
- `bandingkan_segmen` sign convention: `bandingkan_segmen(nilai[0:8], nilai[8:16])` == `mean(seg2) - mean(seg1)`,
  not the reverse.
- A composite step referencing a prior result via `langkah{N}` binding resolves correctly (e.g.
  `rasio(nilai[15], langkah1)` after a step 1 that produced a scalar).
- Referencing a **non-scalar** step's `langkah{N}` (e.g. a `deteksi_anomali` result) is rejected.
- Referencing a **forward** `langkah{N}` (N ≥ current step's own index) is rejected.

## Acceptance

- No `# ponytail` markers remain in `operations.py`.
- New tests pass; full `pytest` suite green.
- No change to `verify_sample`'s public behavior for existing passing tests (Lampiran B/D fixtures still
  score 100% / 66.7%).

## Comments

- Filed from ADR-0003 follow-up issue 1 (`docs/adr/0003-finalize-operation-semantics-and-grounding-tolerance.md`).
- The forward-reference / non-scalar-binding rejection may require a small `verifier.py` change (the current
  `resolve_token` doesn't validate either) — that's in scope here, it's enforcing ADR-0003 Item 4, not a new
  design decision.
