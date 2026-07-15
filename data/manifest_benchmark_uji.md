# Manifest — Benchmark Uji (F2-01)

Deret time series **real, khusus uji** untuk RQ1/RQ2. File data JSONL ada di
`data/processed/benchmark_uji.jsonl` (gitignored); regen dengan
`scripts/fetch_wb.ps1` lalu `python scripts/curate_benchmark_uji.py`.

**Sumber:** World Bank Open Data API untuk Indonesia (IDN) — penerbitan ulang
data resmi Indonesia (BPS, Kemenkes/WHO). Dipilih karena angkanya *eksak* &
dapat diambil andal via API.

**Anti-bocor (§9.4):** agregat tahunan World Bank ini berbeda sumber &
granularitas dari sumber train (PIHPS harian, Kemenkes SKDR mingguan, BMKG).
**Khusus uji — jangan dipakai di train.**

**Tanggal ambil:** 2026-07-15. **Jumlah deret:** 18.

| id | domain | tugas | kesulitan | n | rentang | sumber |
|---|---|---|---|---|---|---|
| uji_kesehatan_mortalitas_balita | kesehatan | tren | easy | 55 | 1970-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SH.DYN.MORT?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_mortalitas_bayi | kesehatan | segmen | easy | 55 | 1970-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SP.DYN.IMRT.IN?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_harapan_hidup | kesehatan | anomali | medium | 55 | 1970-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SP.DYN.LE00.IN?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_mortalitas_ibu | kesehatan | tren | easy | 39 | 1985-2023 | https://api.worldbank.org/v2/country/IDN/indicator/SH.STA.MMRT?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_imunisasi_campak | kesehatan | anomali | medium | 42 | 1983-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SH.IMM.MEAS?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_imunisasi_dpt | kesehatan | penjelasan | medium | 44 | 1981-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SH.IMM.IDPT?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_insiden_tbc | kesehatan | tren | hard | 25 | 2000-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SH.TBS.INCD?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_mortalitas_neonatal | kesehatan | segmen | easy | 55 | 1970-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SH.DYN.NMRT?format=json&per_page=300&date=1970:2024 |
| uji_kesehatan_belanja_kesehatan | kesehatan | anomali | hard | 24 | 2000-2023 | https://api.worldbank.org/v2/country/IDN/indicator/SH.XPD.CHEX.GD.ZS?format=json&per_page=300&date=1970:2024 |
| uji_pangan_indeks_produksi_pangan | pangan-pertanian | tren | easy | 53 | 1970-2022 | https://api.worldbank.org/v2/country/IDN/indicator/AG.PRD.FOOD.XD?format=json&per_page=300&date=1970:2024 |
| uji_pangan_indeks_produksi_tanaman | pangan-pertanian | penjelasan | medium | 53 | 1970-2022 | https://api.worldbank.org/v2/country/IDN/indicator/AG.PRD.CROP.XD?format=json&per_page=300&date=1970:2024 |
| uji_pangan_hasil_serealia | pangan-pertanian | tren | easy | 54 | 1970-2023 | https://api.worldbank.org/v2/country/IDN/indicator/AG.YLD.CREL.KG?format=json&per_page=300&date=1970:2024 |
| uji_pangan_pdb_pertanian | pangan-pertanian | segmen | medium | 42 | 1983-2024 | https://api.worldbank.org/v2/country/IDN/indicator/NV.AGR.TOTL.ZS?format=json&per_page=300&date=1970:2024 |
| uji_pangan_lahan_pertanian | pangan-pertanian | tren | hard | 54 | 1970-2023 | https://api.worldbank.org/v2/country/IDN/indicator/AG.LND.AGRI.ZS?format=json&per_page=300&date=1970:2024 |
| uji_pangan_inflasi | pangan-pertanian | anomali | medium | 55 | 1970-2024 | https://api.worldbank.org/v2/country/IDN/indicator/FP.CPI.TOTL.ZG?format=json&per_page=300&date=1970:2024 |
| uji_pangan_indeks_harga_konsumen | pangan-pertanian | tren | easy | 55 | 1970-2024 | https://api.worldbank.org/v2/country/IDN/indicator/FP.CPI.TOTL?format=json&per_page=300&date=1970:2024 |
| uji_pangan_lahan_subur | pangan-pertanian | penjelasan | hard | 54 | 1970-2023 | https://api.worldbank.org/v2/country/IDN/indicator/AG.LND.ARBL.ZS?format=json&per_page=300&date=1970:2024 |
| uji_pangan_tenaga_kerja_pertanian | pangan-pertanian | segmen | medium | 34 | 1991-2024 | https://api.worldbank.org/v2/country/IDN/indicator/SL.AGR.EMPL.ZS?format=json&per_page=300&date=1970:2024 |
