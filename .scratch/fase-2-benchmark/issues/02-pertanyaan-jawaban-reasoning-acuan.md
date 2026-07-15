# Questions + gold answers + shortest-grounded reference reasoning

Status: needs-info
Difficulty: hard
Depends: F2-01, F1-01

## Spec

For each curated series, produce a full `Sample` (Lampiran A):

1. Write one **question**.
2. Compute the **correct answer** by formula.
3. Synthesize the **reference reasoning** as the **shortest operation chain** where (a) every step grounds
   under the verifier, and (b) the steps together justify the answer (brief v2 §4.2 — the "minimal-sufficient
   grounded chain" that is the training target for adaptive length). No redundant steps.
4. Label task type + difficulty.

## Blocked by

**F1-01** — the reference reasoning uses operations whose semantics (`deteksi_anomali`, `bandingkan_segmen`,
`z_score` population) must be finalized first, because they define label correctness.

## Acceptance

- Each sample verifies at **100% grounding** by construction (`verify_sample`).
- Shortest-chain property checked: removing any step breaks grounding **or** sufficiency.
- Difficulty label present.
- Schema + grounding checks green (hand off to F2-03).

## Comments
