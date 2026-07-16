# QLoRA training setup

Status: needs-triage
Difficulty: medium
Depends: F4-05

## Spec

Stand up the fine-tune pipeline with **Unsloth** (decision D1, `.scratch/CONCERNS.md` — supersedes the
LLaMA-Factory/DeepSpeed plan in brief v2 §4.5 / brief §19), **QLoRA** NF4 4-bit (r 16–64, alpha 32, lr
1e-4–2e-4, cosine+warmup, bf16, 2–3 epochs), fits T4/V100. Notebook under `notebooks/`. Consumes the
converted train file (gearts JSONL → Unsloth chat format, produced with F4-05). Can be scaffolded before the
dataset is final (train on a tiny sample end-to-end first). The actual fine-tune run (F5-02) is handed to the
collaborator with compute.

## Acceptance (finalize at grill time)

- Target: notebook trains on a tiny sample end-to-end; config committed under `experiments/`.

## Comments
