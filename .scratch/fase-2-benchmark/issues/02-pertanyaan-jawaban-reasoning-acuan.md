# Questions + gold answers + shortest-grounded reference reasoning

Status: done (track-b — pending merge ke master)
Difficulty: hard
Depends: F2-01, F1-01

## Spec

For each curated series, produce a full `Sample` (Lampiran A):

1. Write one **question**.
2. Compute the **correct answer** by formula.
3. Synthesize the **reference reasoning** as the **shortest operation chain** where (a) every step grounds
   under the verifier, and (b) the steps together justify the answer (brief v2 §4.2 — the "minimal-sufficient
   grounded chain" that is the training target for adaptive length). No redundant steps.
4. Label task type + difficulty.

## Blocked by

**F1-01** — the reference reasoning uses operations whose semantics (`deteksi_anomali`, `bandingkan_segmen`,
`z_score` population) must be finalized first, because they define label correctness.

## Acceptance

- Each sample verifies at **100% grounding** by construction (`verify_sample`).
- Shortest-chain property checked: removing any step breaks grounding **or** sufficiency.
- Difficulty label present.
- Schema + grounding checks green (hand off to F2-03).

## Comments

### Sesi B (track-b) — selesai

Merge `master` dulu (F1-01/ADR-0003 sudah mendarat) → sintesis acuan mengikuti semantik operasi **final**.

**Hasil:** 18 `Sample` lengkap (pertanyaan konkret + jawaban gold by-formula + reasoning acuan operasi-form),
**semua `grounding_score = 100.0`** diverifikasi `verify_sample`.

**Cara jamin 100% grounded & terpendek:**
- `hasil` tiap langkah **dihitung verifier** (`eval_step`) lalu diverifikasi ulang — grounded by construction,
  bukan ditebak.
- Rantai minimal per tugas: tren / segmen / anomali = **1 langkah**, penjelasan = **2 langkah** (variasi
  panjang = *reasoning adaptif*).
  - tren `slope`; segmen `bandingkan_segmen` (selisih rata-rata bertanda = arah+besar sekaligus);
    anomali `z_score(titik, baseline)`; penjelasan `slope ; persen_naik(awal->akhir)`.
- **Shortest-chain dijaga per-sampel:** tiap langkah dikutip jawaban (`cites`); label penjelasan dibuat
  **komposit** (`{naik|turun}_{besar|kecil}` / `tidak_monoton`) sehingga membuang langkah mana pun mematahkan
  kecukupan di *setiap* sampel — sekaligus menutup bug koherensi (lahan_subur sempat "turun" padahal ujung
  akhir +6,87%).
- **ADR-0003 dipatuhi:** `bandingkan_segmen` = selisih mean skalar (Item 2A); `z_score` ddof=0 dengan
  **populasi baseline eksplisit** pada deret bertren (Item 3C) agar anomali tak terdilusi; `deteksi_anomali`
  (non-skalar) **dihindari** — anomali via `z_score` skalar agar tergrounding penuh (grounding non-skalar =
  urusan F1-05).

**Bukti:** `pytest` → **56 passed** (validasi 18 sampel 100% grounded + panjang = minimum template + tiap
langkah dikutip jawaban + uji logika rantai tanpa network + uji determinisme regen).

**Artefak:**
- `scripts/synthesize_reasoning_acuan.py` — sintesis deterministik (baca `benchmark_uji.jsonl` → tulis acuan).
- `data/processed/benchmark_acuan.jsonl` — 18 sampel lengkap (gitignored, regenerable).
- `data/manifest_benchmark_acuan.md` — **manifest di-commit**: id, tugas, kesulitan, rantai, label, keyakinan.
- `tests/test_synthesize_reasoning_acuan.py`.
- `docs/lab-notebook/2026-07-15-reasoning-acuan-benchmark.md` — desain + hasil + keterbatasan.

**Serah ke F2-03** (schema + grounding sweep + anti-bocor): input siap. **Tidak** memulai F2-03.

**Keterbatasan** (detail di lab-notebook): granularitas tahunan (outbreak mingguan belum ada → F4-02);
tak ada kontrol negatif `tidak_ada_anomali` (4 deret anomali memang beranomali nyata); `deteksi_anomali`
bisa memperkaya anomali begitu F1-05 mendarat (opsional).
