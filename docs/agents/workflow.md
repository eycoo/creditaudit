# Agent Workflow

How work flows through this repo: skills drive the process, sub-agents execute by difficulty, memory captures what was learned. Research phases refer to `project_brief.md` §17 (Fase 1–8).

## The loop

```
   ┌─ 1. DESIGN ────────────────────────────────────────────┐
   │  /grill-me on a brief phase → /to-prd → /to-issues     │
   │  (each issue gets Status: + Difficulty:) → /triage     │
   └────────────────────────┬───────────────────────────────┘
                            ▼
   ┌─ 2. EXECUTE per issue (route by Difficulty) ───────────┐
   │  easy   → scout (lookups) / data-qa (dataset checks)   │
   │  medium → builder (code via /tdd) / writer (prose)     │
   │  hard   → researcher (design, analysis, taxonomy)      │
   │  bugs   → /diagnose                                    │
   └────────────────────────┬───────────────────────────────┘
                            ▼
   ┌─ 3. VERIFY ────────────────────────────────────────────┐
   │  pytest green → /review (Standards + Spec) → commit    │
   └────────────────────────┬───────────────────────────────┘
                            ▼
   ┌─ 4. RECORD (memory — see memory.md) ───────────────────┐
   │  experiment result → docs/lab-notebook/                │
   │  new decision      → docs/adr/                         │
   │  new domain term   → CONTEXT.md                        │
   │  session end       → /handoff                          │
   └────────────────────────────────────────────────────────┘
```

## 1. Design

- **`/grill-me`** — stress-test a phase of the brief (or any plan) before committing to it. Use at the start of every Fase.
- **`/to-prd`** — synthesize the grilled understanding into a PRD at `.scratch/<feature-slug>/PRD.md`.
- **`/to-issues`** — break the PRD into vertical-slice issues under `.scratch/<feature-slug>/issues/`. Set `Difficulty:` on each issue during breakdown (see rubric below).
- **`/triage`** — move issues through the state machine (`needs-triage` → `ready-for-agent` / `ready-for-human` / …).

### Difficulty rubric

| Difficulty | Test | Examples from this project |
|---|---|---|
| `easy` | Answer exists in the repo/data; no judgment, no writes to `src/` | file inventory, label distribution counts, "which samples fail schema validation" |
| `medium` | Well-specified change; spec says exactly what done looks like | extend calculator for `denda_basis`, preprocessing script, render template variant, a laporan section |
| `hard` | Requires design judgment or novel analysis; spec describes the problem, not the solution | injection transform design (Lampiran C), PoT output format, ablation analysis, taxonomy revision |

## 2. Execute — sub-agent routing

Defined in `.claude/agents/`. Delegate; don't do easy work in the main context.

| Agent | Model | When |
|---|---|---|
| `scout` | sonnet | easy read-only lookups, searches, sanity peeks |
| `data-qa` | sonnet | easy recurring dataset checks: schema validation, split leakage (brief §8.6), label stats |
| `builder` | opus | medium implementation issues — always via `/tdd` for non-trivial logic |
| `writer` | opus | medium prose: laporan/paper sections (Indonesian), grounded to `experiments/` results |
| `researcher` | opus | hard issues: design decisions, error analysis, anything that ends in an ADR |

Model policy: **no haiku** — easy → Sonnet, medium/hard → Opus.

Rules of thumb:
- An issue marked `ready-for-agent` must be executable by the routed agent **with no human context** — if it isn't, it's `needs-triage` again.
- `hard` issues often *produce* `medium` issues: researcher designs, builder implements.
- Main-context Claude orchestrates and reviews; sub-agents execute.

## 3. Verify

- `pytest` green before any commit touching `src/` or `tests/`.
- **`/review`** — two parallel axes: Standards (repo conventions, CONTEXT.md vocabulary, ADR compliance) and Spec (does the diff match the originating issue/PRD).
- **`/diagnose`** for any bug: reproduce → minimise → hypothesise → instrument → fix → regression-test.

## 4. Record

See `memory.md` for the full routing rules. Short version: decisions → ADR, experiment outcomes → lab notebook, new vocabulary → CONTEXT.md, session end → `/handoff`.

## Periodic

- **`/improve-codebase-architecture`** — between Fase transitions, once real pipeline code exists.
- **`/zoom-out`** — when entering an unfamiliar area of the code.
- **`/qa`** — conversational bug capture; files issues in the tracker.

## Not used (and why)

- `setup-pre-commit` — Husky/lint-staged is Node-ecosystem; this is a Python repo. Revisit with the `pre-commit` framework if hook automation is wanted.
- GitHub-dependent flows — tracker is local markdown until a remote exists.
