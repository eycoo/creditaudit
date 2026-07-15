# Manifest — Reasoning Acuan Benchmark Uji (F2-02)

Jawaban gold + rantai operasi acuan **terpendek** untuk 18 deret uji (F2-01).
Data JSONL: `data/processed/benchmark_acuan.jsonl` (gitignored); regen dengan
`python scripts/synthesize_reasoning_acuan.py`.

Semantik operasi mengikuti **ADR-0003** (final). Tiap sampel **100% grounded**
oleh konstruksi: `hasil` tiap langkah dihitung verifier lalu diverifikasi ulang.
Rantai = *minimal-cukup* (brief v2 §4.2): tiap langkah dikutip jawaban.

**Jumlah:** 18 sampel. Semua `grounding_score = 100.0`.

| id | tugas | kesulitan | #langkah | rantai operasi | label gold | keyakinan |
|---|---|---|---|---|---|---|
| uji_kesehatan_mortalitas_balita | tren | easy | 1 | `slope(nilai[0:55])` | menurun | tinggi |
| uji_kesehatan_mortalitas_bayi | segmen | easy | 1 | `bandingkan_segmen(nilai[0:27], nilai[27:55])` | paruh_awal_lebih_tinggi | tinggi |
| uji_kesehatan_harapan_hidup | anomali | medium | 1 | `z_score(nilai[51], nilai[44:50])` | ada_anomali | tinggi |
| uji_kesehatan_mortalitas_ibu | tren | easy | 1 | `slope(nilai[0:39])` | menurun | tinggi |
| uji_kesehatan_imunisasi_campak | anomali | medium | 1 | `z_score(nilai[38], nilai[30:37])` | ada_anomali | tinggi |
| uji_kesehatan_imunisasi_dpt | penjelasan | medium | 2 | `slope(nilai[0:44]) ; persen_naik(nilai[0]->nilai[43])` | naik_besar | tinggi |
| uji_kesehatan_insiden_tbc | tren | hard | 1 | `slope(nilai[0:25])` | menurun | sedang |
| uji_kesehatan_mortalitas_neonatal | segmen | easy | 1 | `bandingkan_segmen(nilai[0:27], nilai[27:55])` | paruh_awal_lebih_tinggi | tinggi |
| uji_kesehatan_belanja_kesehatan | anomali | hard | 1 | `z_score(nilai[21], nilai[14:20])` | ada_anomali | tinggi |
| uji_pangan_indeks_produksi_pangan | tren | easy | 1 | `slope(nilai[0:53])` | meningkat | tinggi |
| uji_pangan_indeks_produksi_tanaman | penjelasan | medium | 2 | `slope(nilai[0:53]) ; persen_naik(nilai[0]->nilai[52])` | naik_besar | tinggi |
| uji_pangan_hasil_serealia | tren | easy | 1 | `slope(nilai[0:54])` | meningkat | tinggi |
| uji_pangan_pdb_pertanian | segmen | medium | 1 | `bandingkan_segmen(nilai[0:21], nilai[21:42])` | paruh_awal_lebih_tinggi | tinggi |
| uji_pangan_lahan_pertanian | tren | hard | 1 | `slope(nilai[0:54])` | meningkat | tinggi |
| uji_pangan_inflasi | anomali | medium | 1 | `z_score(nilai[28])` | ada_anomali | tinggi |
| uji_pangan_indeks_harga_konsumen | tren | easy | 1 | `slope(nilai[0:55])` | meningkat | tinggi |
| uji_pangan_lahan_subur | penjelasan | hard | 2 | `slope(nilai[0:54]) ; persen_naik(nilai[0]->nilai[53])` | tidak_monoton | rendah |
| uji_pangan_tenaga_kerja_pertanian | segmen | medium | 1 | `bandingkan_segmen(nilai[0:17], nilai[17:34])` | paruh_awal_lebih_tinggi | sedang |
