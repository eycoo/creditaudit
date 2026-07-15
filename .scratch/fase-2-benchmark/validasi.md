# Validasi Benchmark Uji (F2-03)

Status: **LULUS** — semua kriteria acceptance terpenuhi. Divalidasi 2026-07-15 (Sesi B / track-b) atas
`data/processed/benchmark_acuan.jsonl` (18 sampel, F2-01 + F2-02), semantik operasi ADR-0003 final
(pasca-merge F1-05/F1-06). Regenerasi: `python scripts/synthesize_reasoning_acuan.py`.

## 1. Validasi schema

`Sample.from_dict` + `Sample.validate()` per baris.

| Cek | Hasil |
|---|---|
| Baris total | 18 |
| Gagal parse (`from_dict`) | **0** |
| Gagal validasi (`validate()`) | **0** |
| ID unik | 18/18 |

## 2. Sweep grounding

`gearts.metrics.dataset_grounding(samples)` dan `verify_sample` per sampel.

| Cek | Hasil |
|---|---|
| `dataset_grounding(samples)` | **100.0** |
| Sampel bukan 100% | **0** dari 18 |
| Operasi terpakai | `slope`, `bandingkan_segmen`, `z_score`, `persen_naik` (semua skalar; `deteksi_anomali` non-skalar tak dipakai di acuan — lihat catatan F2-02) |

Tiap `hasil` langkah dihitung ulang verifier saat sintesis (F2-02) sehingga grounded *by construction*;
sweep ini mengonfirmasi ulang di bawah semantik operasi **final** (ADR-0003, pasca F1-05/F1-06) — regenerasi
sebelum validasi memastikan tak ada drift dari perubahan `operations.py`/`verifier.py`.

## 3. Distribusi

**Per jenis tugas** (4 target, brief §6):

| Tugas | Jumlah |
|---|---|
| tren | 7 |
| segmen | 4 |
| anomali | 4 |
| penjelasan | 3 |
| **Total** | **18** |

**Per kesulitan:**

| Kesulitan | Jumlah |
|---|---|
| easy | 7 |
| medium | 7 |
| hard | 4 |
| **Total** | **18** |

**Per domain:**

| Domain | Jumlah |
|---|---|
| kesehatan | 9 |
| pangan-pertanian | 9 |
| **Total** | **18** |

Semua 4 jenis tugas & ketiga tingkat kesulitan terwakili; tak ada strata kosong. `penjelasan` (n=3) adalah
strata tertipis — dicatat, bukan gagal (ambang acceptance F2-01 hanya "cover varied difficulty/task types",
bukan kuota per-sel).

## 4. Cek anti-bocor (brief §9.4)

Sumber uji: **World Bank Open Data API** (`api.worldbank.org`), agregat **tahunan**, 18/18 sampel.

Sumber train rencana (F4-01 inventaris, `.scratch/fase-1-fondasi/sumber-deret.md`) — tiga sumber **wajib**:

| Domain | Sumber train rencana | Host | Granularitas |
|---|---|---|---|
| food price | PIHPS Nasional (BI) | `bi.go.id/hargapangan` | harian |
| health/DBD | Kemenkes SKDR | `skdr.surveilans.org` / `data.kemkes.go.id` | mingguan |
| weather | BMKG | `dataonline.bmkg.go.id` | harian / per-3-jam |

**Hasil:** tak satu pun dari 18 URL sumber di `data/manifest_benchmark_uji.md` menyentuh host di atas — semua
`api.worldbank.org`. Host, penyedia, dan granularitas **berbeda total** dari ketiga sumber train wajib.
**Cek anti-bocor LULUS.**

**Catatan kehati-hatian (bukan kegagalan, untuk F4-05):** F4-01 juga mencatat **BPS Web API**
(`webapi.bps.go.id`) sebagai sumber train *pelengkap/cadangan* untuk IHK/inflasi bulanan (§4 tabel inventaris,
bukan salah satu dari tiga wajib). Dua sampel uji kita — `uji_pangan_inflasi` (`FP.CPI.TOTL.ZG`) dan
`uji_pangan_indeks_harga_konsumen` (`FP.CPI.TOTL`) — mengukur **fenomena statistik yang sama** (IHK/inflasi
nasional Indonesia) yang aslinya diterbitkan BPS, hanya diterbitkan-ulang tahunan oleh World Bank. Host & baris
data tetap berbeda (tahunan World Bank vs bulanan BPS langsung) sehingga **bukan duplikasi literal** — tapi
jika BPS Web API benar dipakai sebagai sumber train nanti, F4-05 (split anti-bocor) sebaiknya menandai kedua
sampel uji ini sebagai *domain-adjacent*, bukan cuma cek host, untuk kehati-hatian ekstra.

## Kesimpulan

Semua 4 kriteria acceptance (schema, grounding, distribusi, anti-bocor) **lulus**. Benchmark siap dipakai
Fase 3 (RQ1/RQ2, tanpa fine-tune). Tak ada perubahan data (data-qa: verifikasi, tidak memperbaiki).

**Bukti tes:** `pytest` → **72 passed**, termasuk `tests/test_validasi_benchmark.py` (regresi guard: schema
0-gagal, `dataset_grounding == 100.0`, cakupan strata, tanpa host train di manifest).
