# BOARD — master task list (awal → akhir)

The full research arc, start to finish, for the Gemastik project. Every session **starts here**.

- **Current plan:** [`project_brief_v2.md`](../project_brief_v2.md) (sharpened gap, RQ1–RQ4, experiments, 5-day plan).
- **Canonical spec / Lampiran:** [`project_brief.md`](../project_brief.md) (JSONL schema + operation library the code keys on).
- **How work is routed:** [`docs/agents/workflow.md`](../docs/agents/workflow.md).

> **Fase numbering:** the Fase 1–6 grouping below is *this board's own* and is authoritative. It supersedes the brief's older Tahap 1–6 (`project_brief.md` §9–§14) and §18 timeline — plan from this board, not from those. (Note: `project_brief.md` §17 is *Ethics/Legal*, not a phase list.)

## How to use this board (for a new / parallel session)

1. Read this table. Pick an issue whose **Status is `ready-for-agent`** and whose **`Depends:` are all `done`**.
2. Open its file, do the work via the routed agent (see Difficulty → agent below), keep `pytest` green.
3. **Claim it** so other sessions don't collide: set the issue's `Status:` to `in-progress` (add your session note), and flip it to `done` here when merged.
4. If an issue is not executable with no human context, it is **not** `ready-for-agent` — leave it `needs-triage`.

**Difficulty → agent:** `easy` → `scout` / `data-qa` · `medium` → `builder` (code) / `writer` (prose) · `hard` → `researcher`. Model policy: no haiku.

**Status values:** `done` · `ready-for-agent` (executable now) · `needs-info` (blocked by an upstream issue) · `ready-for-human` (needs the user: a decision, model access, or compute) · `needs-triage` (real work, not yet fully specified — expand via `/grill-me` + `/to-issues` when its fase is reached).

## Parallel tracks (what can run at the same time without colliding)

- **Track A — Verifier/method:** F1-01, F1-04, F1-05, F1-06
- **Track B — Benchmark:** F2-01 → F2-02 → F2-03
- **Track C — Experiments (no fine-tune):** F3-01 → F3-02, F3-03
- **Track D — Dataset:** F4-01 → F4-02 → F4-03 → F4-04 → F4-05
- **Track E — Fine-tune + heavy experiments:** F5-01 → F5-02 → F5-03, F5-04
- **Track F — Paper:** F6-01, F6-02 (now) → F6-03, F6-04 → F6-05

**Startable right now, in parallel, zero collision:** `F1-05`, `F1-06` (both unblocked by F1-01 as of
2026-07-15), `F3-01` (harness), `F4-01` (source inventory), `F6-01` (paper positioning), `F6-02` (verify
citations). `F1-01` is **done** (ADR-0003 Accepted, committed on `track-a`, not yet merged to `master` —
Sessions B/D still need `git merge master` after integration before touching F2-02/F4-04).

## Parallel run (4 sessions) — coordination

Four sessions run at once, one per track, each in its own **git worktree** so they never collide on
files. They share one `.git` and coordinate only through `master`. The **main folder** (`backup_gems`) stays
on `master` and is the **integration point**.

| Session | Track | Worktree · branch | Wave-0 task (start now) | Waits on |
|---|---|---|---|---|
| A | Verifier | `../gems-A` · `track-a` | F1-01 done, F1-04 done → next: F1-05, F1-06 | — |
| B | Benchmark | `../gems-B` · `track-b` | F2-01 | F2-02 ← F1-01 + F2-01 |
| C | Experiments | `../gems-C` · `track-c` | F3-01 | F3-02/03 ← F2-03 + model access |
| D | Dataset | `../gems-D` · `track-d` | F4-01 → F4-02 | F4-04 ← F1-01 + F4-03 |

**Protocol (every session):**

1. **Claim** — set the issue's `Status: in-progress` before working; flip to `done` here when merged.
2. **Ship** — issue done + `pytest` green → commit on the track branch.
3. **Integrate** — from the **main folder** (`backup_gems`, on `master`): `git merge track-x`. Do **not**
   `git checkout master` inside a worktree — `master` is checked out in the main folder, so it will refuse.
4. **Sync** — before starting a task whose `Depends:` just cleared, inside the worktree run
   `git merge master` to pull the finalized upstream work.
5. **The F1-01 gate** — F1-01 unblocks F2-02, F1-05, and F4-04 across three tracks. The moment it lands on
   `master`, Sessions A/B/D `git merge master` before touching those. **Do F1-01 first.**

## Fase 1 — Foundation: verifier + operation library

| ID | Task | Difficulty | Status | Depends | File |
|---|---|---|---|---|---|
| F1-01 | Finalize operation semantics + grounding tolerance (**blocker** for synthesis & non-scalar grounding) | hard | done | — | [fase-1-fondasi/issues/01](fase-1-fondasi/issues/01-finalisasi-pustaka-operasi.md) |
| F1-04 | Tolerance sensitivity sweep + verifier validation writeup | easy | done | — | [fase-1-fondasi/issues/04](fase-1-fondasi/issues/04-uji-sensitivitas-toleransi.md) |
| F1-05 | Non-scalar grounding (`deteksi_anomali` via index-set / Jaccard) | medium | ready-for-agent | — | [fase-1-fondasi/issues/05](fase-1-fondasi/issues/05-grounding-non-skalar.md) |
| F1-06 | Lock finalized operation semantics in code + tests (ADR-0003 follow-up) | medium | ready-for-agent | — | [fase-1-fondasi/issues/06](fase-1-fondasi/issues/06-lock-operasi-semantik.md) |

## Fase 2 — Small test benchmark (feeds RQ1 / RQ2)

| ID | Task | Difficulty | Status | Depends | File |
|---|---|---|---|---|---|
| F2-01 | Curate 15–30 real test series (1–2 mature domains) | medium | ready-for-agent | — | [fase-2-benchmark/issues/01](fase-2-benchmark/issues/01-kurasi-deret-uji.md) |
| F2-02 | Questions + gold answers + shortest-grounded reference reasoning | hard | needs-info | F2-01, F1-01 | [fase-2-benchmark/issues/02](fase-2-benchmark/issues/02-pertanyaan-jawaban-reasoning-acuan.md) |
| F2-03 | Validate benchmark (schema, grounding sweep, no leakage) | easy | needs-info | F2-01, F2-02 | [fase-2-benchmark/issues/03](fase-2-benchmark/issues/03-validasi-benchmark.md) |

## Fase 3 — Experiments without fine-tune (RQ1, RQ2) — cheap, Day 1

| ID | Task | Difficulty | Status | Depends | File |
|---|---|---|---|---|---|
| F3-01 | Experiment harness (model adapter → verifier → 3 metrics → tables/curve) | medium | ready-for-agent | — | [fase-3-eksperimen-tanpa-finetune/issues/01](fase-3-eksperimen-tanpa-finetune/issues/01-harness-eksperimen.md) |
| F3-02 | Experiment 1 — baseline hallucination test (RQ1) | medium | ready-for-human | F3-01, F2-03 | [fase-3-eksperimen-tanpa-finetune/issues/02](fase-3-eksperimen-tanpa-finetune/issues/02-eksperimen-1-halusinasi-rq1.md) |
| F3-03 | Experiment 2 — grounding-vs-token curve (RQ2, the novelty) | hard | ready-for-human | F3-01, F2-03 | [fase-3-eksperimen-tanpa-finetune/issues/03](fase-3-eksperimen-tanpa-finetune/issues/03-eksperimen-2-kurva-rq2.md) |

## Fase 4 — Full dataset (for fine-tune)

| ID | Task | Difficulty | Status | Depends | File |
|---|---|---|---|---|---|
| F4-01 | Inventory of public series sources | easy | ready-for-agent | — | [fase-1-fondasi/issues/03](fase-1-fondasi/issues/03-inventaris-sumber-deret.md) |
| F4-02 | One-source scraper → JSONL | medium | ready-for-agent | F4-01 | [fase-1-fondasi/issues/02](fase-1-fondasi/issues/02-scraper-satu-sumber.md) |
| F4-03 | Full scrape of chosen domains | medium | needs-triage | F4-02 | [fase-4-dataset/issues/03](fase-4-dataset/issues/03-scrape-penuh.md) |
| F4-04 | Large-scale reasoning synthesis + auto-verify | hard | needs-triage | F4-03, F1-01 | [fase-4-dataset/issues/04](fase-4-dataset/issues/04-sintesis-reasoning-acuan.md) |
| F4-05 | Train/test split + stratify + anti-leakage (§9.4) | medium | needs-triage | F4-04 | [fase-4-dataset/issues/05](fase-4-dataset/issues/05-split-anti-bocor.md) |

> Note: F4-01/F4-02 physically live under `fase-1-fondasi/issues/` (kept there so historical lab-notebook links stay valid); they belong to the Data track.

## Fase 5 — Fine-tune + heavy experiments (RQ3, RQ4)

| ID | Task | Difficulty | Status | Depends | File |
|---|---|---|---|---|---|
| F5-01 | QLoRA training setup (LLaMA-Factory + ZeRO-2 notebook) | medium | needs-triage | F4-05 | [fase-5-finetune-eksperimen/issues/01](fase-5-finetune-eksperimen/issues/01-setup-qlora.md) |
| F5-02 | Fine-tune Qwen2.5-7B | medium | ready-for-human | F5-01 | [fase-5-finetune-eksperimen/issues/02](fase-5-finetune-eksperimen/issues/02-finetune-qwen.md) |
| F5-03 | Experiment 3 — our method vs baselines B1–B4, grounding-per-token (RQ3) | hard | needs-triage | F5-02, F3-01 | [fase-5-finetune-eksperimen/issues/03](fase-5-finetune-eksperimen/issues/03-eksperimen-3-vs-baseline-rq3.md) |
| F5-04 | Experiment 4 — ablation (RQ4) | hard | needs-triage | F5-02, F3-01 | [fase-5-finetune-eksperimen/issues/04](fase-5-finetune-eksperimen/issues/04-eksperimen-4-ablation-rq4.md) |

## Fase 6 — Paper

| ID | Task | Difficulty | Status | Depends | File |
|---|---|---|---|---|---|
| F6-01 | Rewrite Kesenjangan + Kontribusi (new positioning) | medium | ready-for-agent | — | [fase-6-paper/issues/01](fase-6-paper/issues/01-positioning-kesenjangan-kontribusi.md) |
| F6-02 | Verify all citations (VeriTime, SelfBudgeter, MTBench + adopted methods) | easy | ready-for-agent | — | [fase-6-paper/issues/02](fase-6-paper/issues/02-verifikasi-sitasi.md) |
| F6-03 | Write Metodologi (with citations for adopted methods) | medium | needs-info | F6-02, F1-01 | [fase-6-paper/issues/03](fase-6-paper/issues/03-metodologi.md) |
| F6-04 | Write Hasil (RQ1–4 tables + curve + verifier validation) | medium | needs-info | F3-02, F3-03, F5-03, F5-04, F1-04 | [fase-6-paper/issues/04](fase-6-paper/issues/04-hasil.md) |
| F6-05 | Finalize paper (IEEE template, architecture figure, term consistency, official title) | medium | needs-info | F6-01, F6-03, F6-04 | [fase-6-paper/issues/05](fase-6-paper/issues/05-finalisasi.md) |

## Backlog / cleanup notes

- `paper/DraftSementara_KrocoMasStanis.pdf` and `paper/2025_firdaus.pdf` are kept (possible teammate draft / reference paper) — **owner should confirm** before deleting; not removed automatically.
- Far-future issues (`needs-triage`) hold a short spec only; expand them via `/grill-me` → `/to-prd` → `/to-issues` when their fase is reached.
