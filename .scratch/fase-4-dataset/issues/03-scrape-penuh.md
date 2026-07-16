# Full scrape of chosen domains

Status: done
Difficulty: medium
Depends: F4-02

## Spec

Scale the single-source scraper (F4-02) to collect the full set of series for the 1–2 chosen **train**
domains, normalized to `Series` JSONL (brief §9.1, §10.1). Expand via `/to-issues` once F4-02 lands and the
domains are fixed.

## Acceptance (finalize at grill time)

- Target: N series per domain, all valid `Series`, provenance logged, public-data only.

## Comments

- **Done (2026-07-17, ADR-0005).** Sumber real dipilih = **BPS Web API** (bukan PIHPS/Bapanas — lihat probe di
  CONCERNS C5). Adapter `src/gearts/scrapers/bps.py` (network di-isolasi, konstruksi-key `datacontent` +
  normalisasi pure, `tests/test_scraper_bps.py` 13 lolos). `scripts/synthesize_train_real.py` menarik **143
  deret nyata** (5 indikator BPS, per-provinsi, tahunan) → **572 sampel train 100% grounded, anti-bocor 0**.
  Digabung sintetik (ADR-0004) → `data/train_unsloth.jsonl` 1172. Provenance: prefix id `train_bps_*`.
- Pengayaan lanjutan (opsional, tak blocking): BPS **bulanan** (dimensi `turth` — inflasi/wisman, anomali
  COVID kaya) + **Bapanas harian** via Playwright (key frontend gated).
