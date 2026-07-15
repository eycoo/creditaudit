# QLoRA training setup

Status: needs-triage
Difficulty: medium
Depends: F4-05

## Spec

Stand up the fine-tune pipeline: LLaMA-Factory + DeepSpeed ZeRO-2 + PEFT, **QLoRA** NF4 4-bit (r 16–64,
alpha 32, lr 1e-4–2e-4, cosine+warmup, bf16, 2–3 epochs), fits T4/V100 (brief v2 §4.5, brief §19). Notebook
under `notebooks/`. Can be scaffolded before the dataset is final (train on a tiny sample end-to-end first).

## Acceptance (finalize at grill time)

- Target: notebook trains on a tiny sample end-to-end; config committed under `experiments/`.

## Comments
