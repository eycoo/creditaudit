# Manifest — Train Set (F4-04)

Deret **terkontrol semi-sintetik** + reasoning operasi-form, **100% grounded**
oleh konstruksi (verifier in-the-loop; langkah tak-ground di-drop). Regen dengan
`python scripts/synthesize_train.py`.

**Anti-bocor (§9.4):** deret sintetik frekuensi tinggi (harian/mingguan/bulanan),
domain mikro — beda `id`, nama, sumber, & granularitas dari benchmark uji (WB tahunan makro).
**Khusus train — tak beririsan dengan test.**

**Jumlah:** 360 sampel (drop 0). Semua `grounding_score = 100.0`.

- per tugas: {'tren': 90, 'segmen': 90, 'anomali': 90, 'penjelasan': 90}
- per kesulitan: {'easy': 120, 'medium': 120, 'hard': 120}
- per label: {'meningkat': 29, 'menurun': 34, 'relatif_stabil': 27, 'paruh_akhir_lebih_tinggi': 28, 'paruh_awal_lebih_tinggi': 26, 'setara': 36, 'ada_anomali': 45, 'tidak_ada_anomali': 45, 'naik_besar': 37, 'turun_besar': 34, 'tidak_monoton': 7, 'turun_kecil': 7, 'naik_kecil': 5}
