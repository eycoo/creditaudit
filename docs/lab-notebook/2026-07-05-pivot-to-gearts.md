# 2026-07-05 — Pivot to GEAR-TS

> Supersedes the project scope of the 2026-07-04 entry (credit-audit), which is kept as history.

## Hypothesis

n/a — pivot entry. Records the wholesale change of project and the re-scoping of the two ADRs.

## Setup

Project pivoted from credit-offer misleading-detection to **GEAR-TS** (grounded, token-efficient, verifiable
LLM reasoning over time series; new `project_brief.md`). The workflow/memory/agent infrastructure was
domain-agnostic and kept; the domain code, glossary, ADRs, issues, and brief were replaced. Package
`creditaudit` → `gearts`. ADR-0001 and ADR-0002 were **re-scoped** (not reversed): the decision "separate the
language model from a deterministic checker" carries over unchanged — old "program-of-thought + calculator" is
now "operation-constrained reasoning + verifier". Files renamed to match.

## Result

- New seed code (`src/gearts/`): `schema` (JSONL, Lampiran A), `operations` (library, Lampiran C), `verifier`
  (deterministic grounding), `metrics`.
- **Verifier reproduces Lampiran B**: honest reasoning on the DBD series `[12…78]` scores grounding **100%**.
- **Verifier catches Lampiran D hallucination**: claiming +30% where the series rose +105% flags that step and
  drops grounding to **66.7%**.
- Grounding tolerance set to `max(abs_tol, rel_tol·|expected|)` (defaults 0.01/0.01) — a calibration knob so a
  presented `105.3` grounds against a recomputed `105.26`, while magnitude errors do not. See ADR-0002.
- 20/20 tests green.

## Conclusion

Foundation matches brief Fase 1 (operation library + JSONL schema + verifier). Remaining Fase-1 work is pinning
the ambiguous operation semantics (needs human domain judgment).

## Next

- `.scratch/fase-1-fondasi/issues/01-finalisasi-pustaka-operasi.md` (hard, human)
- `.scratch/fase-1-fondasi/issues/02-scraper-satu-sumber.md` (medium, agent)
- `.scratch/fase-1-fondasi/issues/03-inventaris-sumber-deret.md` (easy, agent)
