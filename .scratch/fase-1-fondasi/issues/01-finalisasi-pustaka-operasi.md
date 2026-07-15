# Finalisasi pustaka operasi + semantik grounding

Status: ready-for-human
Difficulty: hard
Depends: —

## Problem

The operation library (`src/gearts/operations.py`, brief Lampiran C) is implemented, but several operations
have provisional semantics that must be pinned before large-scale reasoning synthesis (Fase 3), because they
define the ground truth for the whole dataset (brief §18: Fase 1 + 3 are the decisive points):

1. `deteksi_anomali(ambang, pop)` — currently "|z| > ambang over the full series". Decide: population window
   (whole series vs rolling), one-sided vs two-sided, and what its `hasil` in a JSONL step should be (index?
   list? count?) — since it returns non-scalar, grounding treatment is undecided (`# ponytail` in code).
2. `bandingkan_segmen(r1, r2)` — currently `mean(r2) − mean(r1)`. Decide: difference vs ratio vs percent, and
   whether it returns one number or a small struct.
3. `z_score` population — whole series vs a baseline window (matters when the series is trending).
4. **Composite operations** — how (or whether) steps may reference prior step results by name (the verifier
   supports `langkah{N}` bindings today; the brief's Lampiran C shows `rasio(nilai[15], baseline)`). Define the
   naming convention.
5. **Grounding tolerance** — confirm `max(abs_tol, rel_tol·|expected|)` with defaults 0.01/0.01, or set
   per-operation tolerances.

## Why human

These are domain-judgment + measurement-validity calls that set the label contract for every downstream sample.
`researcher` can prepare a decision doc with options + recommendations, but the final call is the user's.

## Acceptance

- `CONTEXT.md` operation table updated with finalized semantics.
- An ADR (Status: Accepted) recording the operation library + grounding-tolerance decision.
- `# ponytail` markers in `operations.py`/`verifier.py` resolved or converted to `medium` follow-up issues.
- Tests updated to lock the finalized semantics.

## Comments
