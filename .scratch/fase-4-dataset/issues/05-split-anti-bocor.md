# Train/test split + stratify + anti-leakage

Status: needs-triage
Difficulty: medium
Depends: F4-04

## Spec

Split into **train** (mostly semi-synthetic) and **test** (mostly real), stratified by task + difficulty,
with anti-leakage: no test source appears in train (brief §9.4). The Fase-2 benchmark is the real test core.

## Acceptance (finalize at grill time)

- Target: split manifest; leakage check passes (data-qa); distribution tables.

## Comments
