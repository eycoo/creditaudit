# Manifest — TRAIN Acuan (F4-04)

Train set fine-tune: rantai operasi acuan **terpendek** atas deret
**sintetis-terkendali** (ADR-0004). Data JSONL:
`data/synthetic/train_acuan.jsonl`; regen dengan
`python scripts/synthesize_train_acuan.py`.

**Jumlah:** 336 sampel. Semua `grounding_score = 100.0` (verifier
di dalam loop; sampel tak-grounded dibuang & dibangkitkan ulang —
41 percobaan dibuang saat pembangkitan). Label bersih by construction.

**Anti-bocor (9.4):** deret dibangkitkan sendiri, **lepas** dari 18 deret
WB sumber test; 18 deret uji dibandingkan, **0 tabrakan numerik**.

## Distribusi tugas x kesulitan

| tugas \ kesulitan | easy | medium | hard | total |
|---|---|---|---|---|
| tren | 28 | 28 | 28 | 84 |
| segmen | 28 | 28 | 28 | 84 |
| anomali | 28 | 28 | 28 | 84 |
| penjelasan | 28 | 28 | 28 | 84 |
| **total** | 112 | 112 | 112 | 336 |

## Distribusi label gold

| label | jumlah |
|---|---|
| ada_anomali | 56 |
| meningkat | 30 |
| menurun | 26 |
| naik_besar | 10 |
| naik_kecil | 13 |
| paruh_akhir_lebih_tinggi | 25 |
| paruh_awal_lebih_tinggi | 31 |
| relatif_stabil | 28 |
| setara | 28 |
| tidak_ada_anomali | 28 |
| tidak_monoton | 28 |
| turun_besar | 18 |
| turun_kecil | 15 |

## Panjang rantai (langkah)

| #langkah | jumlah |
|---|---|
| 1 | 252 |
| 2 | 84 |

## Domain

| domain | jumlah |
|---|---|
| cuaca | 36 |
| energi | 36 |
| kesehatan | 132 |
| pangan-pertanian | 132 |
