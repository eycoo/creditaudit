# Experiment 4 — ablation (RQ4)

Status: ready-for-human (run box)
Difficulty: hard
Depends: F5-02, F3-01

## Spec

Turn off one component at a time and measure the effect on grounding / tokens / accuracy (brief v2 §5,
Experiment 4):
- operation format (→ free prose)
- shortest-grounded-chain target (→ arbitrary length)
- adaptivity
- fine-tune

## Acceptance (finalize at grill time)

- Target: ablation table isolating each component's contribution.

## Implementation (code ready — run on box)

`experiments/exp4_rq4.py` (+ `experiments/methods.py`). Writes
`experiments/rq4/tabel_rq4.{csv,md}`. Starts from the full method and turns off one
component at a time (each maps to a component in the design):

| variant | change from Kami | isolates |
|---|---|---|
| Kami-penuh | — (LoRA · operation · shortest-grounded) | — |
| -finetune | base model instead of LoRA | fine-tune |
| -format_operasi | free prose instead of operations | operation format |
| -target_terpendek | `mode="panjang"` (verbose) | shortest-grounded objective |
| -adaptif | fixed `max_steps=1` for every item | per-task length adaptation |

Notes:
- `-adaptif` fixes a 1-step budget so tasks that genuinely need 2 steps (penjelasan)
  break — that gap is the cost of not adapting. `-target_terpendek` keeps operations but
  drops the "as few as possible" objective.
- Same raw-output token accounting + grounding-per-token column as RQ3 (see issue 03).

Run: set `GEARTS_LORA_PATH`, then `python experiments/exp4_rq4.py` on the A6000.

## Comments
