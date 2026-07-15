# 2026-07-15 — Reasoning acuan benchmark uji (F2-02)

## Tujuan

Untuk 18 deret uji F2-01 (`data/processed/benchmark_uji.jsonl`), hasilkan tiap `Sample` lengkap:
pertanyaan konkret, jawaban gold (by formula), dan **reasoning acuan operasi-form terpendek** yang tiap
angkanya lolos verifier (brief v2 §4.2, "minimal-sufficient grounded chain"). Semantik operasi mengikuti
**ADR-0003** (final).

## Metode

Sintesis deterministik (`scripts/synthesize_reasoning_acuan.py`): tiap langkah `hasil`-nya **dihitung oleh
verifier** (`eval_step`) lalu diverifikasi ulang (`verify_sample`) → grounding 100% *by construction*, bukan
ditebak. `hasil` dibulatkan 3 desimal (jauh di dalam toleransi `0.01/0.01`, ADR-0003 Item 5). `deteksi_anomali`
**dihindari** (non-skalar, grounding-nya urusan F1-05); anomali diekspresikan lewat `z_score` skalar agar
tergrounding penuh sekarang.

### Template rantai minimal per jenis tugas

| Tugas | Rantai | #langkah | Justifikasi kecukupan |
|---|---|---|---|
| tren | `slope(nilai[0:N])` | 1 | tanda+laju slope mengkarakterisasi arah tren |
| segmen | `bandingkan_segmen(nilai[0:h], nilai[h:N])` | 1 | selisih rata-rata bertanda = arah (tanda) + besar (magnitudo) sekaligus |
| anomali | `z_score(nilai[i], baseline)` | 1 | z titik ekstrem vs baseline = seberapa tak-biasa |
| penjelasan | `slope(...)` ; `persen_naik(nilai[0]->nilai[N-1])` | 2 | arah (slope) **dan** kelas besaran (persen) — keduanya wajib untuk label |

**Kenapa hanya penjelasan yang 2 langkah** (variasi panjang = mekanisme *reasoning adaptif*, CONTEXT.md):
label penjelasan dibuat **komposit** — `{naik|turun}_{besar|kecil}`, atau `tidak_monoton` bila tanda slope
dan tanda perubahan ujung-ke-ujung berlawanan. Dengan begitu **membuang langkah mana pun mematahkan
kecukupan** di *setiap* sampel (bukan cuma sebagian): tanpa slope tak ada arah/uji-monoton, tanpa persen tak
ada kelas besaran/uji-monoton. Ini juga menutup bug koherensi awal (lahan_subur sempat berlabel "turun"
padahal ujung akhir lebih tinggi +6,87%).

### Anomali: pemilihan titik & baseline (ADR-0003 Item 3C)

Deret bertren pakai **populasi baseline eksplisit** (jendela sebelum peristiwa) supaya anomali tak terdilusi
tren; deret volatil-stasioner (inflasi) pakai seluruh deret.

| Deret | titik (idx) | baseline | peristiwa |
|---|---|---|---|
| harapan_hidup | 51 | `nilai[44:50]` | penurunan COVID-19 |
| imunisasi_campak | 38 | `nilai[30:37]` | penurunan cakupan COVID-19 |
| belanja_kesehatan | 21 | `nilai[14:20]` | lonjakan belanja COVID-19 |
| inflasi | 28 | seluruh deret | hiperinflasi krisis 1998 |

## Hasil

- **18/18 sampel `grounding_score = 100.0`.** Panjang rantai ∈ {1, 2}; keempat jenis tugas terisi.
- Label gold contoh: mortalitas balita/ibu → `menurun` (tinggi); indeks produksi/IHK → `meningkat`; empat
  deret anomali → `ada_anomali` (|z| 4,9–14,8); lahan_subur → `tidak_monoton` (rendah).
- Manifest di-commit: `data/manifest_benchmark_acuan.md` (id, tugas, kesulitan, rantai, label, keyakinan).
- Tes: `pytest` **56 passed** — termasuk validasi artefak (tiap sampel 100% grounded, panjang = minimum
  template, tiap langkah dikutip jawaban) + uji logika rantai tanpa network + uji determinisme regen.

## Keterbatasan / catatan untuk F2-03 & downstream

- Granularitas **tahunan** → tugas "outbreak" tajam (mingguan) belum terwakili; anomali di sini = titik
  ekstrem tahunan. Bila perlu outbreak mingguan, butuh deret sub-tahunan (scraper langsung, F4-02).
- Rantai sengaja **1 langkah** untuk 3 dari 4 tugas: ini benar-benar *terpendek yang cukup* untuk deret
  jelas; deret ambigu tetap 1 langkah tapi keyakinan turun (mis. insiden_tbc `sedang`), bukan lebih panjang.
  Kalau eksperimen adaptif nanti butuh gradasi panjang lebih halus, itu keputusan sintesis train (F4-04),
  bukan benchmark uji.
- `deteksi_anomali` belum dipakai di acuan; begitu F1-05 (grounding non-skalar) mendarat, sebagian anomali
  bisa diperkaya dengan langkah daftar-indeks — opsional, tak wajib untuk RQ1/RQ2.
- Tidak ada kasus gold `tidak_ada_anomali` (keempat deret anomali memang beranomali nyata). Bila F2-03/penilai
  ingin kontrol negatif, tambah deret tenang sebagai anomali-negatif — di luar lingkup F2-02.
