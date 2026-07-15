# Validate the benchmark

Status: needs-info
Difficulty: easy
Depends: F2-01, F2-02

## Spec (data-qa)

Run the standard dataset health checks on the finished benchmark:

- **Schema validation** on all rows (`Sample.validate`).
- **Grounding sweep**: every reference sample must score **100%** (`dataset_grounding`).
- **Distribution stats**: counts by task type and difficulty.
- **Leakage check**: no test source appears in any planned train source (brief §9.4).

## Acceptance

- 0 schema failures.
- All reference samples 100% grounding.
- Distribution table produced.
- Leakage check passes.
- Summary written to `.scratch/fase-2-benchmark/validasi.md`.

## Comments
