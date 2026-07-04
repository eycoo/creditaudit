# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

Research project scaffolded from `project_brief.md` — a ~500-line brief written in **Indonesian** for a
multimodal system that audits Indonesian digital-credit offers (pinjol, paylater, installment tables) to
reveal true cost and detect misleading fee framing. Phase-1 code lives in `src/creditaudit/` (extraction
schema, deterministic calculator, OJK rule engine); later phases (dataset pipeline, model training) are
tracked as issues in `.scratch/`.

Domain labels are Indonesian and canonical. Keep taxonomy codes, JSON field names, and label strings
**exactly** as the brief spells them (code and data key on them) — the schema is implemented in
`src/creditaudit/schema.py` (mirrors Lampiran A); read `CONTEXT.md` for the glossary before naming anything.

## Commands

```bash
pip install pytest                                   # once
pytest                                               # full suite
pytest tests/test_calculator.py::test_lampiran_b -x  # single test
```

## Agent skills

### Issue tracker

Issues live as local markdown under `.scratch/<feature-slug>/issues/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical defaults (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) as a
`Status:` line, plus a `Difficulty: easy|medium|hard` line. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at root, ADRs in `docs/adr/`. See `docs/agents/domain.md`.

## Workflow & sub-agent routing

Full loop in `docs/agents/workflow.md`: `/grill-me` → `/to-prd` → `/to-issues` → `/triage` → execute →
`/review` → record. Route issues by their `Difficulty:` line — delegate, don't do easy work in main context:

| Difficulty | Agent (`.claude/agents/`) | Model |
|---|---|---|
| easy (lookups) | `scout` | sonnet |
| easy (dataset checks) | `data-qa` | sonnet |
| medium (code, via /tdd) | `builder` | opus |
| medium (Indonesian prose) | `writer` | opus |
| hard (design/analysis) | `researcher` | opus |

Model policy: no haiku anywhere — easy → Sonnet, medium/hard → Opus.

## Memory

Routing rules in `docs/agents/memory.md`. Short version: decisions → `docs/adr/`, experiment outcomes →
`docs/lab-notebook/` (append-only), new domain terms → `CONTEXT.md`, work to do → `.scratch/` issues,
session end → `/handoff`. Project facts always in-repo; harness memory only for user preferences.

## Planned architecture (the load-bearing design)

A **modular pipeline, deliberately not a monolithic VLM.** The core methodological claim: arithmetic is
offloaded to a deterministic calculator because LLMs are unreliable at arithmetic, so audited cost figures
stay accountable. Four sequential modules (`project_brief.md` §10):

```
offer image
  → M1 Perception/Extraction (VLM, Qwen2.5-VL-7B) → JSON financial terms
  → M2 Quantitative Reasoning (reasoning model + calculator) → true effective cost
  → M3 Classification + OJK Compliance → misleading labels + violation flags + severity
  → M4 Explanation Generation (same reasoning model) → plain-Indonesian summary
  → structured audit report
```

- **M2 uses program-of-thought, not plain chain-of-thought:** the model emits a structured calculation
  plan referencing extracted fields; a **deterministic Python calculator executes it.** The dataset teaches
  correct reasoning *structure*; the calculator guarantees correct arithmetic. Both are required — this
  split is the whole point, don't collapse it back into an end-to-end LLM.
- **M3 compliance is rule-based and untrained** (deterministic OJK rule engine); only the misleading-label
  classifier is learned.
- **M4 explanations must be grounded to calculator numbers** so they cannot fabricate figures.

## Hard domain constants (these drive the rule engine and labels)

**OJK compliance thresholds** (M3 rule engine flags violations — verify against current regulation before
relying on them; the brief marks them as versioned):
- Consumptive-loan interest cap: **0.1% per day** (phased target for 2026). Rate above this → flag.
- Lock cap: **total repayment ≤ 100% of principal**. Denda + bunga exceeding 100% of pokok → flag.
- Paylater transparency obligations: POJK 32/2025.

**Misleading-fee taxonomy** — **multi-label and hierarchical** (one offer can carry several). P1–P6 are
cost-misleading categories; R1 is a separate legality red flag:

| Code | Category |
|---|---|
| P1 | Misrepresentasi suku bunga (interest framing) |
| P2 | Biaya siluman (hidden fees / upfront cuts) |
| P3 | Salah basis perhitungan denda (penalty base error) |
| P4 | Penyamaran struktur cicilan (installment disguise) |
| P5 | Framing visual menyesatkan (visual — realized at image-render time) |
| P6 | Klaim palsu atau bait (false "0% / no fee" claims) |
| R1 | Indikator ilegalitas (illegality red flag) |

## Dataset pipeline (the primary contribution)

Two complementary sources (`project_brief.md` §8):
- **Synthetic via CoT-injection:** parametric offer templates → distill correct step-by-step CoT →
  **verify cost with the deterministic calculator** → apply misleading presentation transforms per the
  taxonomy (Lampiran C) that keep the hidden truth computable → emit labeled tuples (offer text, ground-truth
  terms, ground-truth true cost, misleading labels, compliance status, reference CoT). Labels follow the
  transform applied, so they are automatic and exact.
- **Real via scraping** (Play Store, social media, promo material) → manual annotation by ≥2 annotators with
  Cohen/Fleiss kappa → **blur all PII before processing.**
- **Synthetic image rendering** (PIL/Pillow template bank): renders synthetic text into realistic offer
  images so visual misleading (P5) is spatially real.
- **Splits:** train mostly synthetic, **test mostly real** (measures field generalization); stratified by
  misleading category and legality; anti-leakage — test templates/sources must not appear in train.

## Planned stack (`project_brief.md` §18)

Perception `Qwen2.5-VL-7B-Instruct` · Reasoning `Qwen2.5-7B` fine-tuned (IndoMathReason base) · Training
`LLaMA-Factory` + `DeepSpeed ZeRO-2` + `PEFT`, **QLoRA** NF4 4-bit (r 16–64, alpha 32, dropout 0.05, lr
1e-4–2e-4, cosine+warmup, bf16, 2–3 epochs) · OCR fallback `PaddleOCR` · Scraping `Playwright`/`Selenium` ·
Annotation `Label Studio` · Serving `FastAPI` · Logging `Weights & Biases` · Hardware T4/V100 (Colab/Kaggle).

The deterministic **calculator** and **OJK rule engine** are plain Python, not trained.
