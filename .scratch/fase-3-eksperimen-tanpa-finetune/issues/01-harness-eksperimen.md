# Experiment harness

Status: ready-for-agent
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
