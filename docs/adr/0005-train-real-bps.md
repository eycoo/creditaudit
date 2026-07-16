# ADR-0005: Deret TRAIN nyata dari BPS + kebijakan train hibrid (F4-03)

**Status:** Accepted (2026-07-17). **Mengamandemen ADR-0004**: train tak lagi
sintetis-saja. Menambah deret **nyata BPS** sebagai bahan train utama, dengan
sintetis-terkendali sebagai penyeimbang strata. Menghasilkan
`data/synthetic/train_real.jsonl` (572 sampel dari 143 deret nyata) via
`scripts/synthesize_train_real.py` dan adapter `src/gearts/scrapers/bps.py`;
`scripts/to_unsloth.py` kini menggabung real + sintetik → `data/train_unsloth.jsonl`
(**1172** = 572 real + 600 sintetik). Tidak mengubah `operations.py`/`verifier.py`/
`build_reference` — memakai ulang apa adanya (semantik ADR-0003).

## Konteks

Ini lomba **data mining**: kualitas & pemrosesan data nyata berbobot nilai (concern
user C5). ADR-0004 menunda F4-03 (scrape) dan memakai deret sintetis-terkendali,
sambil mencatat "scrape nyata menyusul memperkaya, bukan prasyarat". Probe kelayakan
(2026-07-17) membuka jalur real yang bersih.

## Keputusan

**1. Sumber real = BPS Web API (`webapi.bps.go.id`), bukan PIHPS/Bapanas/BMKG.**
Hasil probe live: **PIHPS** (BI) endpoint internal mati/tak ada API resmi;
**Bapanas** Panel Harga v2 key-gated keras (key frontend publik pun ditolak →
interceptor/recaptcha); **BMKG** publik hanya prakiraan jangka-pendek. **BPS**
menang: REST JSON resmi, key gratis terdaftar, ToS jelas, dan **provider berbeda
dari World Bank** (sumber TEST) → anti-bocor §9.4 bersih secara struktural.

**2. Series real → reasoning lewat `build_reference` yang SAMA → verifier di dalam
loop.** Tiap deret provinsi jadi bahan keempat tugas; `hasil` tiap langkah dihitung
ulang `eval_step`, `verify_sample` di-assert 100%; sampel tak-grounded dibuang.
Definisi grounding train ≡ test. **Label & kesulitan MUNCUL dari data** (tanpa
reject-sampling yang memaksa strata). Untuk ANOMALI, titik dugaan dipilih jujur:
baseline = jendela awal `nilai[0:b]` (b≈60%) yang mengecualikan titik uji, titik =
indeks paling ekstrem di ekor; verifier lalu memutuskan `ada_anomali`/`tidak` via
`|z|>3`. Ini menangkap guncangan nyata (COVID-2020: `ada_anomali` 62 vs `tidak` 81)
tanpa menyuntik apa pun.

**3. Train HIBRID (real headline + sintetik penyeimbang).** Real 572 menjawab
kredibilitas data-mining + memberi label emergent jujur; sintetik 600 (ADR-0004)
menyeimbangkan sel yang jarang muncul di data real (mis. `naik_besar` cuma 6,
`easy` 57). Keduanya 100% grounded + anti-bocor (0 tabrakan lawan 18 deret uji).
Provenance terbaca dari prefix id: `train_bps_*` (real) vs `train_*` (sintetik).

## Konsekuensi & batasan (di-disclose di paper)

- **Deret real = tahunan, n≈10, per-provinsi** dari 5 indikator (kemiskinan P0,
  jumlah miskin, garis kemiskinan, pengangguran terbuka, gini). Deret satu indikator
  antar-provinsi **berkorelasi** — diakui; keragaman struktur (turun/naik/stabil/
  fluktuatif) dipilih sengaja lintas indikator.
- **Kesulitan emergent timpang** (medium/hard dominan) — cermin ambiguitas nyata
  deret pendek; sintetik menyeimbangkan, bukan menyembunyikan. Distribusi nyata
  dilaporkan di `data/manifest_train_real.md`.
- **BPS bulanan (dimensi `turth`) belum ditangani** → malam ini annual saja.
  Deret bulanan (inflasi, wisman — anomali COVID kaya) = pengayaan lanjutan.
- **Kunci API = credential; repo PUBLIC** → dibaca dari env `BPS_API_KEY`/getpass,
  **tak pernah** di-hardcode/commit. Adapter mengisolasi network; konstruksi key
  `datacontent` + normalisasi murni & di-unit-test (`tests/test_scraper_bps.py`).
- Generalisasi lapangan tetap dibuktikan di **test real held-out** (World Bank);
  train real BPS memperkuat, test tetap penilai transfer.

## Alternatif yang ditolak

- **PIHPS / Bapanas / BMKG** sebagai sumber real: mati / key-gated keras /
  jangka-pendek (lihat Keputusan 1). Ditolak malam ini; Bapanas harian layak dikejar
  nanti via Playwright.
- **Train real-saja (572)**: sel label tipis (`naik_besar` 6) melemahkan sinyal
  latih; hibrid lebih seimbang. Ditolak.
- **Tetap sintetik-saja (ADR-0004)**: cukup untuk belajar format, tapi lemah untuk
  klaim kualitas-data lomba data-mining. Diamandemen, bukan dibuang (sintetik tetap
  dipakai sebagai penyeimbang).
