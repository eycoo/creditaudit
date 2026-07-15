# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

Research project for the **Gemastik data-mining competition**, scaffolded from `project_brief.md` (a brief
written in **Indonesian**): grounded, token-efficient, verifiable LLM reasoning over **time series**. An LLM
emits reasoning as a sequence of *operations* over a numeric series; a **deterministic verifier** recomputes
each operation on the original series and checks the claimed number. Phase-1 code lives in `src/gearts/`
(JSONL schema, operation library, verifier, metrics); later phases (data scraping, synthesis, model
training) are tracked as issues in `.scratch/`; the competition paper lives in `paper/`.
`PENJELASAN_PROJECT.md` is a plain-language Indonesian explainer derived from the brief + `CONTEXT.md` —
keep it in sync when framing changes.

**Current plan vs canonical spec — read this before planning any work.** `project_brief_v2.md` is the
**current research plan**: the post-judge-critique revision that sharpens the gap (*keep reasoning grounded
while the token budget is cut*), defines RQ1–RQ4, the experiment design, and a 5-day work plan. Read it for
*what we are doing now*. `project_brief.md` is retained as the **canonical spec / appendix source** — its
Lampiran A (JSONL schema) and Lampiran C (operation library) are what `src/gearts/` and the tests key on.
Read it for *definitions*, not current framing, and do **not** plan off its older plan (its Tahap 1–6 in
§9–§14, or the §18 timeline). The
**master task list is `.scratch/BOARD.md`** — every session starts there, picks a `ready-for-agent` issue
whose `Depends:` are all done, and claims it by updating its `Status:`.

**Two names, strict scoping.** The official research title — used in the paper, README, and all
public-facing prose — is *"Peningkatan Keandalan dan Efisiensi Token LLM pada Data Time Series melalui
Pendekatan Verifikasi Deterministik"*. **GEAR-TS** is the internal working name only (package `gearts`,
brief, issues, ADRs) and must **never** appear in paper prose — the paper sells a method, not a product.

Domain terms are Indonesian and canonical. Keep operation names, JSONL field names, and label strings
**exactly** as the brief spells them (code and data key on them) — the schema is in `src/gearts/schema.py`
(mirrors Lampiran A), the operations in `src/gearts/operations.py` (Lampiran C). Read `CONTEXT.md` for the
glossary before naming anything.

## Commands

```bash
pip install numpy pytest                                        # once
pytest                                                          # full suite
pytest tests/test_verifier.py::test_lampiran_b_full_grounding -x  # single test
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

## Paper (`paper/`)

Current draft: `Makalah_Gemastik_PenalaranTimeSeries.docx`. Route paper writing through the `writer` agent — its conventions
(`.claude/agents/writer.md`) are binding: official title only (never "GEAR-TS"), passive voice
("diusulkan", not "kami mengusulkan"), the official IEEE template's named styles and 2-column layout
(`paper/[Template] Makalah Gemastik ieee.docx`, tables ≤ 8.5 cm), numeric citations `[n]` at clause end
(concept first — not "VeriTime [3] adalah …"), foreign terms in *italics* (model/work names upright).

`arsitektur_sistem.tex` (standalone TikZ, compile with `pdflatex`) is the editable source of the
`arsitektur_sistem.png` figure embedded in the makalah — edit the .tex, don't touch the PNG by hand.

## Memory

Routing rules in `docs/agents/memory.md`. Short version: decisions → `docs/adr/`, experiment outcomes →
`docs/lab-notebook/` (append-only), new domain terms → `CONTEXT.md`, work to do → `.scratch/` issues,
session end → `/handoff`. Project facts always in-repo; harness memory only for user preferences.

## Architecture (the load-bearing design)

**Two separate components, not a monolithic LLM** (ADR-0001). The core claim: an LLM is unreliable at
arithmetic, so it never owns the numbers — it proposes operations, and an external deterministic program
computes and checks them, keeping reasoning auditable (`project_brief.md` §8).

```
numeric series + question
  → LLM (fine-tuned, Qwen2.5-7B class) emits reasoning as a sequence of operations
  → deterministic verifier recomputes each operation on the original series
  → compares recomputed vs claimed (within tolerance) → grounding score + validated reasoning
  → final answer
```

- **Reasoning is operation-form, not free prose (ADR-0002).** Each step names an operation from the fixed
  library (`operations.py`); the **verifier** (`verifier.py`) re-executes it. The dataset teaches reasoning
  *structure*; the verifier guarantees the arithmetic. Both required — don't collapse into an end-to-end LLM.
- **The verifier is the single source of grounding truth**, used in three places: dataset cleaning
  (drop steps that don't verify), evaluation (grounding score), and optionally as an RL reward.
- **Adaptive reasoning length** is the token-efficiency mechanism: clear series → short reasoning,
  ambiguous → long (SelfBudgeter idea brought to time series).

## Key facts (drive the code)

- **Grounding score** (main metric, `project_brief.md` §14): % of scalar reasoning steps whose recomputed
  value matches the claimed one. A step grounds if `|recomputed − claimed| ≤ max(abs_tol, rel_tol·|recomputed|)`.
  The relative term is a **calibration knob** — it lets a presented `105.3` pass against a recomputed `105.26`
  while a real magnitude error (`30` vs `105`) fails. Defaults `abs_tol=rel_tol=0.01`.
- **Operation library** (`operations.py`, Lampiran C): `rata2`, `delta`, `persen_naik`, `rasio`, `slope`,
  `min`/`max`, `z_score`, `deteksi_anomali`, `bandingkan_segmen`. `deteksi_anomali`/`bandingkan_segmen` have
  provisional semantics — finalized by issue `01-finalisasi-pustaka-operasi` (`# ponytail` markers in code).
- **Three metrics**, all deterministic (no LLM judge): answer accuracy, grounding score, token efficiency.

## Dataset pipeline (the primary contribution — `project_brief.md` §9)

- **Numeric series** scraped from real Indonesian public sources: PIHPS/Bank Indonesia (food prices),
  Kemenkes dashboards (disease cases), BMKG (weather), open energy load. Not Kaggle datasets.
- **Reasoning layer (the moat, the laborious part):** for each series, pose a question, compute the correct
  answer by formula, and synthesize operation-form reasoning **whose every number the verifier checks** —
  steps that don't verify are fixed or dropped, so labels are clean by construction.
- **Semi-synthetic for scale, real for test:** train mostly semi-synthetic (real or controlled series +
  auto-verified reasoning); **test mostly real series** to prove field generalization. Stratified by task
  and difficulty; anti-leakage — test sources must not appear in train (§9.4).
- **Format:** JSONL, one sample per line (Lampiran A). Read/write via `gearts.schema`.

## Planned stack (`project_brief.md` §19)

Model `Qwen2.5-7B` fine-tuned · Training `LLaMA-Factory` + `DeepSpeed ZeRO-2` + `PEFT`, **QLoRA** NF4 4-bit
(r 16–64, alpha 32, lr 1e-4–2e-4, cosine+warmup, bf16, 2–3 epochs) · Verifier plain Python + `NumPy`
(untrained) · optional Time-LLM-style series encoder for long series · Scraping `Playwright`/`Selenium` +
official source APIs · Logging `Weights & Biases` · Hardware T4/V100 (Colab/Kaggle). Optional extension: RL
with verifiable grounding reward.

Comparators (`project_brief.md` §7): **VeriTime** (verifiable TS reasoning — main baseline), **SelfBudgeter**
(adaptive token budget), **MTBench** (framing). Our wedge: verifiable **plus** token-efficient, on a
self-built Indonesian dataset.
