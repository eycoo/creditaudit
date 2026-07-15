# Experiment 1 — baseline hallucination test (RQ1)

Status: ready-for-human
Difficulty: medium
Depends: F3-01, F2-03

## Spec

Run existing models (Qwen2.5-7B **without** fine-tune; if possible one GPT-class model) on the test
benchmark. Measure grounding + accuracy.

**Expected result:** decent accuracy but **low grounding** — the models are often right for the wrong
reasons. This is the evidence that the problem (RQ1) is real (brief v2 §5, Experiment 1).

## Needs human

Model access / compute: local GPU, Colab/Kaggle, or an API key. The harness (F3-01) is ready; this is
unblocked for execution the moment a model adapter + access is provided. Cheap — no fine-tune, runnable Day 1.

## Acceptance

- Table `model × (accuracy, grounding)` written under `experiments/`.
- Dated lab-notebook entry.
- Result feeds F6-04 (Hasil).

## Comments
