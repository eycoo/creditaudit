# Manifest — TRAIN Real BPS (F4-03)

Train set fine-tune atas **deret nyata BPS** (Badan Pusat Statistik).
Data JSONL: `data/synthetic/train_real.jsonl` (gitignored); regen dengan
`BPS_API_KEY=... python scripts/synthesize_train_real.py`.

**Deret real:** 143 (per-provinsi, 5 indikator BPS).
**Sampel:** 572 (deret × tugas yang 100% grounded).
Semua `grounding_score = 100.0` (verifier di dalam loop). Label bersih by
construction; **label & kesulitan MUNCUL dari data** (bukan reject-sampling).

**Anti-bocor (§9.4):** sumber test = World Bank; BPS provider beda. 18 deret uji dibandingkan numerik, **0 tabrakan** (diverifikasi runner).

## Indikator sumber (BPS)

| var | freq | catatan struktur |
|---|---|---|
| 192 | tahunan | persentase penduduk miskin (P0) — cenderung menurun |
| 185 | tahunan | jumlah penduduk miskin — cenderung menurun |
| 182 | tahunan | garis kemiskinan — naik kuat |
| 543 | tahunan | tingkat pengangguran terbuka — fluktuatif (guncangan COVID) |
| 98 | tahunan | gini ratio — relatif stabil |

## Distribusi tugas

| tugas | jumlah |
|---|---|
| tren | 143 |
| segmen | 143 |
| anomali | 143 |
| penjelasan | 143 |

## Distribusi kesulitan (emergent, dari keyakinan)

| kesulitan | jumlah |
|---|---|
| easy | 57 |
| medium | 319 |
| hard | 196 |

## Distribusi label gold

| label | jumlah |
|---|---|
| ada_anomali | 62 |
| meningkat | 30 |
| menurun | 86 |
| naik_besar | 6 |
| naik_kecil | 23 |
| paruh_akhir_lebih_tinggi | 23 |
| paruh_awal_lebih_tinggi | 61 |
| relatif_stabil | 27 |
| setara | 59 |
| tidak_ada_anomali | 81 |
| tidak_monoton | 15 |
| turun_besar | 35 |
| turun_kecil | 64 |
