# Validate the benchmark

Status: done (track-b — pending merge ke master)
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

### Sesi B (track-b) — selesai (LULUS)

Merge `master` dulu (F1-05/F1-06 mendarat sejak F2-02) → regenerasi `benchmark_acuan.jsonl` untuk pastikan
tak ada drift dari semantik operasi final, lalu validasi.

**Hasil (detail: `.scratch/fase-2-benchmark/validasi.md`):**
1. **Schema:** 18/18 baris lolos `Sample.from_dict` + `validate()`. 0 gagal.
2. **Grounding:** `dataset_grounding(samples) == 100.0`; tiap sampel individual juga 100%.
3. **Distribusi:** tugas tren 7 / segmen 4 / anomali 4 / penjelasan 3; kesulitan easy 7 / medium 7 / hard 4;
   domain kesehatan 9 / pangan-pertanian 9. Semua 4 tugas & 3 kesulitan terwakili.
4. **Anti-bocor:** sumber uji = `api.worldbank.org` (tahunan) — tak menyentuh host mana pun dari tiga sumber
   train wajib (PIHPS `bi.go.id/hargapangan` harian, Kemenkes SKDR `skdr.surveilans.org` mingguan, BMKG
   `dataonline.bmkg.go.id`). **Lulus.** Catatan kehati-hatian (bukan gagal): 2 sampel (`inflasi`, `IHK`)
   domain-adjacent dengan sumber train *cadangan* BPS Web API (fenomena sama, host & granularitas beda) —
   ditandai untuk F4-05 kalau BPS dipakai jadi sumber train nanti.

**Artefak:**
- `.scratch/fase-2-benchmark/validasi.md` — ringkasan lengkap (di-commit).
- `tests/test_validasi_benchmark.py` — regresi guard read-only (skip bila artefak belum ada); tak mengubah
  data (kontrak data-qa).

**Bukti tes:** `pytest` → **72 passed**.

Benchmark **siap** untuk Fase 3 (F3-02/F3-03, RQ1/RQ2). Tidak ada perbaikan data diperlukan.
