# Experiment 3 — our method vs baselines (RQ3)

Status: needs-triage
Difficulty: hard
Depends: F5-02, F3-01

## Spec

Compare our method against four baselines (brief v2 §5, Experiment 3):
- **B1** free-prose LLM (no operations)
- **B2** long operation reasoning, no length control (honest proxy for the VeriTime direction)
- **B3** short but grounding-blind (SelfBudgeter direction, on time series)
- **B4** pure statistics (compute-only, no explanation)

Headline metric: **grounding-per-token**. Baseline definitions are design calls — expand via `/grill-me`
(→ `researcher`).

## Acceptance (finalize at grill time)

- Target: table all methods × (accuracy, grounding, tokens) + grounding-per-token comparison.

## Comments
