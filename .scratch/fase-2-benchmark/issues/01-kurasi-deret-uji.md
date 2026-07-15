# Curate small real test benchmark (series only)

Status: done (track-b — pending merge ke master)
Difficulty: medium
Depends: — (may consume F4-01 inventory if it exists)

## Spec

Hand-curate **15–30 real** time series from **1–2 mature** Indonesian public domains (recommended: Kemenkes
disease/DBD weekly + PIHPS food prices), as `Series` JSONL matching `src/gearts/schema.py`.

This is the **test** benchmark for RQ1/RQ2, so it must be real (field generalization) and **test-only**:
these sources must **not** reappear in the future train set (anti-leakage, brief §9.4). Record provenance
(source URL + retrieval date) per series.

- Series + minimal context/question **stub** only — no reasoning yet (that is F2-02).
- Cover varied difficulty: some clear-trend series, some ambiguous / with distractors.
- Span the four task types in the question stubs: anomaly/outbreak, trend characterization, segment
  comparison, explanation.

## Constraints

- Public data only; respect source ToS; no personal data.
- Every row must pass `Series` construction.

## Acceptance

- ≥ 15 real series, each valid `Series`.
- Provenance (source + date) recorded per series.
- Data under `data/` (gitignored), plus a small **committed** manifest listing source, date, task type,
  difficulty per series.
- No overlap with any planned train source.

## Comments

### Sesi B (track-b) — selesai

**Hasil:** 18 deret real (≥15 ✓) dari **2 domain matang**: `kesehatan` (9) + `pangan-pertanian` (9),
tiap baris `Sample` valid (series + stub konteks/pertanyaan, `reasoning: []`, `jawaban` stub — F2-02 isi).

**Sumber & keputusan (menyimpang dari rekomendasi PIHPS/Kemenkes — sengaja):**
- Dashboard PIHPS/Kemenkes hanya melayani param-API/PDF/SPA; angka *eksak* sulit diambil andal. Menuliskan
  angka hampiran di bawah label sumber real = risiko integritas → dihindari.
- Dipakai **World Bank Open Data API (IDN)** yang menerbitkan ulang data resmi Indonesia (BPS, Kemenkes/WHO)
  sebagai angka **eksak** via API. Nilai diambil verbatim, bukan diringkas model.
- **Anti-bocor (§9.4) malah lebih bersih:** agregat *tahunan* World Bank beda sumber & granularitas dari
  sumber train (PIHPS harian, Kemenkes SKDR mingguan, BMKG). Ditandai **khusus uji** di manifest.

**Cakupan:** 4 jenis tugas semua ada (anomali/tren/segmen/penjelasan); kesulitan easy/medium/hard; deret
tren-jelas (mis. mortalitas balita turun) + deret ambigu/bising (mis. lahan pertanian nyaris datar, belanja
kesehatan bising, inflasi volatil). Rentang 24–55 titik/deret, tahunan.

**Artefak:**
- `scripts/fetch_wb.ps1` — ambil JSON mentah → `data/raw/` (gitignored). Network di-sandbox harness; jalan manual.
- `scripts/curate_benchmark_uji.py` — bangun `Sample` JSONL + manifest dari data mentah (deterministik, no network).
- `data/processed/benchmark_uji.jsonl` — 18 deret (gitignored, regenerable).
- `data/manifest_benchmark_uji.md` — **manifest di-commit**: id, domain, tugas, kesulitan, n, rentang, URL sumber, tanggal ambil (2026-07-15).
- `tests/test_curate_benchmark_uji.py` — logika build (tanpa network) + validasi artefak JSONL.

**Bukti tes:** `python -m pytest` → **27 passed** (termasuk validasi 18 deret: tiap `Series` lolos `validate()`,
`reasoning` kosong sesuai lingkup F2-01).

**Batas lingkup:** granularitas tahunan (bukan mingguan/harian). Jika F2-02/penilai ingin deret sub-tahunan
(mis. DBD mingguan) untuk tugas outbreak yang lebih tajam, perlu scraper sumber langsung (lihat F4-02) — di
luar lingkup issue ini. **Tidak** memulai F2-02 (nunggu F1-01).
