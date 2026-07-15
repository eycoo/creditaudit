# Experiment harness

Status: in-progress
Difficulty: medium
Depends: —

## Spec

Build the evaluation harness that all model experiments run through. Given a benchmark JSONL and a model's
per-item output (reasoning + answer), it:

- runs `verify_sample` on each item;
- computes the **three metrics**: `answer_accuracy`, grounding score (`dataset_grounding`), reasoning tokens
  (`count_reasoning_tokens`);
- emits per-model tables **and** the `(tokens, grounding, accuracy)` records the RQ2 curve (F3-03) needs.

Model access is **pluggable** via an adapter: a `predict(sample) -> (reasoning_steps, answer)` callable. Ship
a `MockModel` (canned outputs) so the harness is fully testable offline **now**. Real adapters
(Qwen2.5-7B local/Colab; an API model) are added in F3-02 / F3-03.

The output format is the contract F6-04 (Hasil) consumes — keep it stable and documented.

## Notes

- Swap `count_reasoning_tokens`' whitespace proxy for the real model tokenizer here (`# ponytail` in
  `metrics.py`).

## Acceptance

- Harness runs end-to-end on the benchmark with `MockModel`.
- Produces a metrics table + a per-item `(tokens, grounding, accuracy)` record.
- Unit test on a tiny fixture; `pytest` green.

## Comments

**F3-01 done (track-c).** New module `src/gearts/harness.py` — imports `verifier`
+ `metrics` only, no series arithmetic of its own (ADR-0002); `verifier.py`/`metrics.py`
untouched.

- **Adapter contract:** `predict(sample) -> (reasoning_steps, answer_label)`.
  `MockModel` ships canned per-id outputs → fully offline-testable now. Real
  Qwen2.5-7B / API adapters land in F3-02/F3-03.
- **Flow:** adapter proposes reasoning → harness rebuilds the item with that reasoning
  over the **original** series → `verify_sample` recomputes (model never owns numbers).
- **Output contract (F6-04 consumes, keep stable):** `run_model` → `ModelResult`
  {per-item `ItemResult`, `answer_accuracy`, `mean_grounding`, `mean_tokens`};
  `metrics_table(results)` → one dict row/model; `curve_records(result)` → per-item
  `(tokens, grounding, accuracy)` triples for the RQ2 curve.
- **Tests:** `tests/test_harness.py` (7 cases: perfect/hallucinating models, verifies
  vs original series, curve triples, table, empty benchmark). `pytest` green — 26 passed.
- Tokenizer swap note (`# ponytail` in `metrics.py`) still stands — plug the real model
  tokenizer at F3-02/F3-03 eval time.

Not started: F3-02/F3-03 (wait on F2-03 + model access).
