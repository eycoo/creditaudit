# Scraper satu sumber deret → JSONL

Status: ready-for-agent
Difficulty: medium
Depends: F4-01 (inventory)

## Spec

Build one end-to-end scraper that turns a real public source into `Series` JSONL matching
`src/gearts/schema.py`. Default source: **PIHPS / Bank Indonesia** daily food price (brief §9.1). Steps:

- Fetch via official API/endpoint (prefer API over HTML scraping; Playwright only if no API).
- Normalize per brief §10.1: standardize unit (`satuan`), frequency (`freq`), handle missing values, number format.
- Emit `Series` objects (`nama`, `satuan`, `freq`, `nilai`) written to `data/raw/<source>.jsonl` via
  `gearts.schema.write_jsonl`.
- Do **not** synthesize reasoning here — series only. Reasoning synthesis is a separate Fase-3 issue.

## Constraints

- Respect the source's ToS; public data only (brief §17.1). No personal data.
- Series values land as clean numeric arrays; log and skip malformed rows.

## Acceptance

- Running the scraper produces a valid JSONL file; every row passes `Series` construction.
- A test on a small fixture asserts normalization (unit/freq set, missing values handled).
- `pytest` green.

## Comments
