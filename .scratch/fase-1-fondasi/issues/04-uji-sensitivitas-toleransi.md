# Tolerance sensitivity sweep + verifier validation

Status: in-progress
Difficulty: easy
Depends: —

> Session A (track-a, 2026-07-15): full grid sweep abs_tol x rel_tol over
> {0, 0.001, 0.01, 0.05, 0.1} (25 combos), honest + hallucinated Lampiran B.
> Script: experiments/tolerance-sweep/sweep.py. Entry: docs/lab-notebook/2026-07-15-tolerance-sweep.md.

## Spec

A small, reproducible experiment that does two things (both are real paper results — brief v2 §5
"Hasil fondasi" and §4.4 "kritik 2b"), and needs **no model**:

1. **Verifier validation.** Show the verifier reproduces the Lampiran B honest reasoning at **100%**
   grounding and flags the Lampiran D hallucination (step 2 claims 30 where the series rose ~105%) down to
   **66.7%**. Reuse the `LAMPIRAN_B` fixture in `tests/test_verifier.py`.
2. **Tolerance sensitivity sweep.** Sweep `rel_tol` ∈ {0.005, 0.01, 0.02, 0.05} (and `abs_tol` likewise) over
   the honest sample and its hallucinated variant. Show the honest score stays 100% at every setting, and the
   30-vs-105 magnitude error stays caught at every setting. This is what justifies the default 0.01 (the
   choice is otherwise unjustified — the judge's technical critique 2b).

## Implementation

- Script under `experiments/tolerance-sweep/` (or `scripts/`), importing `gearts.verifier.verify_sample`.
- Emit a table: `rel_tol` × grounding score, for honest vs hallucinated.
- Write a dated lab-notebook entry `docs/lab-notebook/<date>-tolerance-sweep.md` with the table + one-line
  conclusion ("score stable across tolerances; magnitude error caught at all").

## Acceptance

- Table produced; honest = 100% at all tolerances; hallucination flagged (< 100%) at all tolerances.
- Lab-notebook entry written.
- `pytest` green.

## Comments
