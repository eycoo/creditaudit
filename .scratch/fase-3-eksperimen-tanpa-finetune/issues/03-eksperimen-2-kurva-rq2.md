# Experiment 2 — grounding-vs-token curve (RQ2, the novelty)

Status: ready-for-human
Difficulty: hard
Depends: F3-01, F2-03

## Spec

On existing models, elicit reasoning at **varying lengths** (short vs long prompts, or a step cap). At each
length, measure grounding + accuracy, then plot **both against token count** (brief v2 §5, Experiment 2).

**Expected result:** as reasoning shortens, **grounding falls faster than accuracy**. This is the empirical
hook that justifies the entire gap — efficient reasoning silently drops the auditable steps while the answer
often stays right. It is the single most important early result and needs no fine-tune.

## Needs human

Model access (same as F3-02). Curve analysis is a `researcher` task once the data is collected.

## Acceptance

- Curve produced: grounding vs tokens **and** accuracy vs tokens, with the underlying data table.
- A written finding stating whether grounding degrades faster than accuracy (and by how much).
- Result feeds F6-04 (Hasil) and anchors the Kesenjangan argument (F6-01).

## Comments
