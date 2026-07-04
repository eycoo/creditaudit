# ADR-0002: Program-of-thought with a deterministic calculator

**Status:** Accepted (2026-07-04)

## Context

M2 must compute true effective cost. Chain-of-thought models do arithmetic "in their head" and get it wrong at exactly the multi-step chains this domain requires (pokok → bunga harian → tenor → denda → admin → efektif). Ground-truth labels for the synthetic dataset need the same math, so an inconsistent implementation would poison training data and evaluation simultaneously. (`project_brief.md` §10.2, §8.5.)

## Decision

- The reasoning model emits a **structured calculation plan** (program-of-thought) that references extracted schema fields — it never emits final numbers directly.
- A **deterministic Python calculator** executes the plan. All audited arithmetic lives in `src/creditaudit/calculator.py` and nowhere else.
- The same calculator produces dataset ground truth (brief §8.5) and inference results — single source of truth.
- M4 explanations may only cite numbers present in calculator output (grounding constraint).

## Consequences

- The model learns reasoning *structure*; correctness of arithmetic is guaranteed by construction. Both parts are load-bearing — removing either is the RQ2 ablation, not a refactor.
- `calculator.py` changes affect ground truth, training data, and inference at once: they require regenerating affected dataset splits and a lab-notebook entry.
- Model size can stay at 7B (brief §11) because arithmetic capability is not required of it.
