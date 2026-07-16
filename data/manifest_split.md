# Manifest — Split Train/Test (F4-05)

Split brief 9.4: **train** semi-sintetik untuk skala, **test** deret asli
untuk generalisasi; distratifikasi tugas x kesulitan; sumber uji tak muncul
di train. Seed tetap (F4-04 deterministik) -> reprodusibel.

- **TRAIN** `data/synthetic/train_acuan.jsonl` — 600 sampel, sintetis-terkendali (ADR-0004).
- **TEST** `data/processed/benchmark_acuan.jsonl` — 18 sampel, deret REAL World Bank (F2-01/02).

## Anti-bocor (brief 9.4)

- namespace id disjoint (`train_*` vs `uji_*`): LOLOS.
- identitas numerik deret (train vs 18 deret uji): **0 tabrakan** -> LOLOS.
- sumber beda by construction: train sintetik-terkendali; test World Bank (tahunan makro). Tak ada sumber uji dipakai di train.
- nama indikator train **disjoint** dari 18 nama uji (0 tumpang-tindih).

**Status anti-bocor: LOLOS.**

## Distribusi (tugas x kesulitan)

### TRAIN

| tugas \ kesulitan | easy | medium | hard | total |
|---|---|---|---|---|
| tren | 50 | 50 | 50 | 150 |
| segmen | 50 | 50 | 50 | 150 |
| anomali | 50 | 50 | 50 | 150 |
| penjelasan | 50 | 50 | 50 | 150 |
| **total** | 200 | 200 | 200 | 600 |

### TEST

| tugas \ kesulitan | easy | medium | hard | total |
|---|---|---|---|---|
| tren | 5 | 0 | 2 | 7 |
| segmen | 2 | 2 | 0 | 4 |
| anomali | 0 | 3 | 1 | 4 |
| penjelasan | 0 | 2 | 1 | 3 |
| **total** | 7 | 7 | 4 | 18 |
