# 2026-07-16 — Cross-check independen verifier (C3 / #5)

## Hipotesis

Concern **C3** (#5): verifier membuat label train **dan** menilai eval, jadi reviewer bisa bilang "skor
grounding = apa kata kodemu sendiri" (sirkular). Kalau jalur perhitungan **kedua yang sepenuhnya terpisah**
— parser + rumus ditulis ulang, tanpa menyentuh `gearts.verifier`/`gearts.operations` — menghasilkan
`expected` yang **identik** dengan verifier untuk tiap langkah ter-skor, maka `expected` verifier bukan
artefak satu implementasi, dan tuduhan sirkular pada perhitungan aritmetik gugur.

## Setup

Jalur kedua di `experiments/verifier-crosscheck/independent.py` — **NumPy murni, nol impor `gearts`**
(ditegakkan test). Yang ditulis ulang tangan:

- **parser DSL operasi** (regex sendiri),
- **semantik index/slice**: batas `b` eksklusif + index negatif di-resolve manual (`i<0 → n+i`), bukan
  mengandalkan slicing yang kebetulan sama dengan verifier,
- **rumus operasi** jalur beda: `slope` = OLS `Σ(x-x̄)(y-ȳ)/Σ(x-x̄)²` (bukan `np.polyfit`), std populasi
  (ddof=0) dihitung manual (bukan lewat `z_score`/`deteksi_anomali`), `bandingkan_segmen`/`persen_naik`/
  `z_score` dst. dari rumus tangan.

Orkestrator `crosscheck.py` memanggil `verify_sample` (jalur verifier) + `recompute_sample` (jalur
independen) untuk tiap langkah ter-skor, lalu cocokkan `expected` (skalar: `|Δ| ≤ 1e-6`; set-valued:
kesamaan himpunan). Sumber yang di-cross-check — semua yang punya reasoning:

- `data/processed/benchmark_acuan.jsonl` (18 sampel),
- `data/synthetic/train_acuan.jsonl` (360 sampel) — **inilah data yang justru dibersihkan verifier**, inti
  C3 "bersihin train",
- `data/processed/benchmark_uji.jsonl` (18 sampel) — set uji **telanjang**, reasoning kosong (diisi model
  saat eval), jadi 0 langkah ter-skor secara wajar (bukan bug).

Deterministik, tanpa LLM judge. Semantik toleransi (abs/rel 0.01, Jaccard) dijaga cocok dengan verifier.

## Hasil

| file | langkah ter-skor | match | mismatch | match% |
|---|---|---|---|---|
| benchmark_acuan.jsonl | 21 | 21 | 0 | 100.00% |
| benchmark_uji.jsonl | 0 | 0 | 0 | n/a (reasoning kosong) |
| train_acuan.jsonl | 450 | 450 | 0 | 100.00% |
| **TOTAL** | **471** | **471** | **0** | **100.00%** |

Operasi tercakup: `slope`, `persen_naik`, `z_score`, `bandingkan_segmen` (data nyata) + `rata2`, `rasio`,
`delta`, `deteksi_anomali` (set-valued), `langkah{N}` refs (fixture Lampiran B/D, DETEKSI, COMPOSITE lewat
pytest). **0 mismatch** → tak ditemukan bug verifier pada set ini.

Artefak audit manusia: `experiments/verifier-crosscheck/spotcheck.csv` — 10 langkah **grounded** (nyata dari
train, `sumber=benchmark`) + 10 **ungrounded** (perturbasi deterministik klaim jauh di luar toleransi,
`sumber=perturbasi`, sebab benchmark verifier-clean tak punya ungrounded alami), kolom
`cocok_menurut_auditor` kosong untuk diisi manusia.

pytest: **89 passed** (4 test baru `tests/test_crosscheck_independent.py`: jalur independen == verifier di
Lampiran B/DETEKSI/COMPOSITE + guard "independent.py tak impor gearts").

## Kesimpulan

Dua jalur perhitungan yang independen sepakat **471/471 = 100%** pada seluruh langkah ter-skor termasuk 450
langkah data-latih yang dibersihkan verifier → `expected` verifier bukan artefak sirkular; tuduhan
"grounding = kata kodemu sendiri" gugur untuk komponen aritmetik. Sisa C3 (agreement label pada output model
**asli**) menunggu keluaran model dari track eval.
