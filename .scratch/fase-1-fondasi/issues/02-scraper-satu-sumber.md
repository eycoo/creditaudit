# Scraper satu sumber deret → JSONL

Status: in-progress
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

- Sesi D (Opus, F4-02, TDD): PIHPS/Bank Indonesia daily food-price scraper landed.
  - New module `src/gearts/scrapers/pihps.py`: thin network `fetch_pihps` (stdlib `urllib`, no new deps —
    prefers the BI grid endpoint over Playwright per issue) split from **pure, tested** `parse_id_number` +
    `records_to_series`. Also `src/gearts/scrapers/__init__.py` and a CLI (`python -m gearts.scrapers.pihps`).
  - Normalization (brief §10.1): Indonesian number format (`.`=thousands, `,`=decimal → `"13.100,50"`=13100.5),
    missing/malformed values (`""`, `"-"`, `None`, junk) logged and **skipped** to keep `nilai` a clean numeric
    array (no fabricated fill), chronological sort, `satuan` + `freq="harian"` set. Empty-after-clean raises.
  - **Schema extension** (`schema.py`): added `write_series_jsonl`/`read_series_jsonl`. Rationale + deviation:
    the issue says "emit Series via `write_jsonl`", but `write_jsonl` only serializes full `Sample`s, and raw
    scraped series have no reasoning/question/answer yet (ADR-0002 — reasoning synthesis is a later phase).
    Storing bare `Series` in `data/raw/` avoids fabricating `Sample` fields. Symmetric read/write, roundtrip-tested.
  - No reasoning synthesized (out of scope). No live scrape run — `PIHPS_ENDPOINT`/response shape flagged for
    re-verification in `sumber-deret.md`; `fetch_pihps` isolates that fragile step so tests stay offline.
  - Tests: `tests/test_scraper_pihps.py` (fixture asserts number parse, missing-value drop, unit/freq set,
    date sort, finite floats, empty-raises, Series JSONL roundtrip). **`pytest` = 34 passed.** CLI `--help` exit 0.
