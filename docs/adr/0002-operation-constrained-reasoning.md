# ADR-0002: Operation-constrained reasoning + deterministic verifier

**Status:** Accepted (2026-07-04, re-scoped to GEAR-TS 2026-07-05)

## Context

Grounding requires that each reasoning step's number be checkable. Free-prose chain-of-thought does
arithmetic "in its head" and gets it wrong on exactly the multi-step chains time-series reasoning needs
(baseline → percent change → ratio → anomaly). The same computation produces the dataset's ground-truth
labels, so an inconsistent implementation would poison training data and evaluation at once
(`project_brief.md` §9.2, §11.2).

## Decision

- The model emits reasoning as a sequence of **operations** drawn from a fixed library (Lampiran C,
  `src/gearts/operations.py`) — e.g. `persen_naik(nilai[11]->nilai[15])` — with a claimed numeric result per
  step. It never emits final numbers by free generation.
- A **deterministic verifier** (`src/gearts/verifier.py`) parses each operation, re-executes it on the
  original series, and compares recomputed vs claimed within tolerance. All recomputation lives here and
  nowhere else.
- The **same verifier** is the single source of grounding truth in three places: dataset cleaning (drop steps
  that don't verify), evaluation (grounding score), and optionally as an RL reward.

## Consequences

- The model learns reasoning *structure*; arithmetic correctness is guaranteed by construction. Both parts
  are load-bearing — removing either is the RQ4 ablation, not a refactor.
- Grounding tolerance is `max(abs_tol, rel_tol·|recomputed|)` (defaults 0.01/0.01). The relative term is a
  deliberate calibration knob so presentation rounding grounds while magnitude errors do not — tuning it is a
  real decision, not an accident.
- Changes to `operations.py`/`verifier.py` affect ground truth, training data, and evaluation simultaneously:
  they require regenerating affected dataset splits and a lab-notebook entry.
- Model size can stay at 7B (`project_brief.md` §12) because arithmetic is not required of it.
