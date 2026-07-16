# Manifest — TRAIN Acuan (F4-04)

Train set fine-tune: rantai operasi acuan **terpendek** atas deret
**sintetis-terkendali** (ADR-0004). Data JSONL:
`data/synthetic/train_acuan.jsonl`; regen dengan
`python scripts/synthesize_train_acuan.py`.

**Jumlah:** 600 sampel. Semua `grounding_score = 100.0` (verifier
di dalam loop; sampel tak-grounded dibuang & dibangkitkan ulang —
68 percobaan dibuang saat pembangkitan). Label bersih by construction.

**Anti-bocor (9.4):** deret dibangkitkan sendiri, **lepas** dari 18 deret
WB sumber test; 18 deret uji dibandingkan, **0 tabrakan numerik**.

## Distribusi tugas x kesulitan

| tugas \ kesulitan | easy | medium | hard | total |
|---|---|---|---|---|
| tren | 50 | 50 | 50 | 150 |
| segmen | 50 | 50 | 50 | 150 |
| anomali | 50 | 50 | 50 | 150 |
| penjelasan | 50 | 50 | 50 | 150 |
| **total** | 200 | 200 | 200 | 600 |

## Distribusi label gold

| label | jumlah |
|---|---|
| ada_anomali | 100 |
| meningkat | 55 |
| menurun | 45 |
| naik_besar | 20 |
| naik_kecil | 20 |
| paruh_akhir_lebih_tinggi | 53 |
| paruh_awal_lebih_tinggi | 47 |
| relatif_stabil | 50 |
| setara | 50 |
| tidak_ada_anomali | 50 |
| tidak_monoton | 50 |
| turun_besar | 30 |
| turun_kecil | 30 |

## Panjang rantai (langkah)

| #langkah | jumlah |
|---|---|
| 1 | 450 |
| 2 | 150 |

## Domain

| domain | jumlah |
|---|---|
| cuaca | 48 |
| energi | 48 |
| kesehatan | 168 |
| pangan-pertanian | 144 |
| pariwisata | 48 |
| perdagangan | 48 |
| telekomunikasi | 48 |
| transportasi | 48 |
