# Large-scale reasoning synthesis + auto-verify

Status: needs-triage
Difficulty: hard
Depends: F4-03, F1-01

## Spec

Automate synthesis of **shortest-grounded reference reasoning** over the scraped series at scale, with the
verifier **in the loop**: steps that don't ground are fixed or dropped, so labels are clean by construction
(brief v2 §4.3). Attach difficulty + task-type labels. This is a design task — expand via `/grill-me`
(→ `researcher`, likely an ADR on the synthesis policy).

## Acceptance (finalize at grill time)

- Target: every sample verifies at 100% grounding; distribution stratified by task + difficulty.

## Comments
