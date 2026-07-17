# Experiment 3 — our method vs baselines (RQ3)

Status: ready-for-human (run box)
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

## Implementation (code ready — run on box)

`experiments/exp3_rq3.py` (+ `experiments/methods.py`; LoRA wired in
`src/gearts/adapters/qwen_vllm.py`). Runnable defaults — semantics still refinable via
`/grill-me`. Writes `experiments/rq3/tabel_rq3.{csv,md}`.

Concrete method definitions used:
- **B1-prosa** — base model, free-prose prompt (`prompt_style="prosa"`), no operations
  → ~0 grounding by construction.
- **B2-veritime** — base model, operation form, `mode="panjang"` (verbose, no length control).
- **B3-selfbudget** — base model, operation form, `mode="pendek"` (brief, grounding-blind).
- **B4-statistik** — no model; `StatBaselineAdapter` computes the label deterministically
  from the series formulas, emits **no** reasoning (0 tokens, grounding N/A). Compute-only floor.
- **Kami** — fine-tuned LoRA, operation form, `mode="pendek"` (shortest-grounded, on-distribution
  with the F5-01 training prompt).

Decisions worth a grill check:
- Baselines B1–B3 run on the **base** model (they represent external approaches); the
  fine-tune's effect is isolated in RQ4. B3 ≈ RQ4's `-finetune` by design (consistency).
- **Tokens counted from raw model output** (whitespace words), not parsed steps — required
  so free-prose (B1) isn't scored as "0 tokens". Fair across prose vs operation form.
- B4 uses whole-series population for anomaly z-score; on the acuan-18 it scores ~88.9%
  accuracy and misses 2 trend-diluted anomalies (gold used an explicit baseline window) —
  an honest limitation of naive pure-stats, kept as-is.

Run: set `GEARTS_LORA_PATH` to the adapter folder, then `python experiments/exp3_rq3.py`
on the A6000 (LoRA served on full-precision base — see `experiments/README-kaggle.md`).

## Comments
