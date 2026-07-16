# Menjalankan eksperimen RQ1/RQ2 di Kaggle (vLLM)

Kode eksperimen (`exp1_rq1.py`, `exp2_rq2.py`, adapter `gearts.adapters.qwen_vllm`) sudah
lengkap dan lolos test **offline**. Model asli (Qwen2.5-7B-Instruct) tidak dijalankan di
laptop — dijalankan di **Kaggle GPU** lewat vLLM. Berikut langkahnya.

## Prasyarat

- Kaggle notebook, **Accelerator: GPU** (T4 cukup; 2×T4 lebih lega), **Internet: ON**.
- Model diunduh otomatis oleh vLLM (`Qwen/Qwen2.5-7B-Instruct`).

## Langkah

1. **Bawa repo ke Kaggle** — clone, atau upload repo sebagai *dataset* lalu `cd` ke root repo.

2. **Install vLLM:**
   ```bash
   pip install -q vllm numpy
   ```

3. **Sediakan data benchmark.** `load_benchmark()` membaca `data/processed/benchmark_acuan.jsonl`
   (18 baris, gitignored — tidak ikut `git clone`). Dua cara:
   - **Termudah:** generate file itu di laptop (`python scripts/synthesize_reasoning_acuan.py`),
     lalu **upload** ke Kaggle dan taruh di `data/processed/benchmark_acuan.jsonl`.
   - **Atau regen di Kaggle** (Linux): ambil data mentah World Bank via Python, lalu
     `python scripts/curate_benchmark_uji.py && python scripts/synthesize_reasoning_acuan.py`.
     (`scripts/fetch_wb.ps1` itu PowerShell/Windows — di Linux ganti dengan ambil URL World Bank
     di manifest pakai `requests` ke `data/raw/wb_<code>.json`.)

4. **Jalankan (dari root repo):**
   ```bash
   python experiments/exp1_rq1.py     # RQ1 -> experiments/rq1/tabel_rq1.{csv,md}
   python experiments/exp2_rq2.py     # RQ2 -> experiments/rq2/kurva_rq2.{csv,md} + records_rq2.csv
   ```

5. **Ambil hasil:** unduh isi `experiments/rq1/` dan `experiments/rq2/`, commit balik ke repo.
   Tabel/kurva ini yang dikonsumsi paper (F6-04) dan dianalisis agent `researcher` (temuan RQ2:
   grounding turun lebih cepat dari accuracy).

## OOM: Qwen2.5-7B fp16 (~14.3 GB) tidak muat di 1×T4 (16 GB)

Bobot model saja hampir memenuhi satu T4, jadi tak ada sisa untuk KV cache → `CUDA out
of memory` saat load. `gpu_memory_utilization`/`max_model_len` **tidak** menolong (yang
overflow bobotnya, bukan cache). Dua jalur, dan notebook `kaggle_rq1_rq2.ipynb`
**memilihnya otomatis** dari jumlah GPU:

- **2×T4 (rekomendasi):** `tensor_parallel_size=2` — bobot dibagi dua GPU, **presisi
  penuh** (baseline paling bersih). Pilih accelerator **GPU T4 x2**.
- **1×T4:** fallback ke model **AWQ 4-bit** `Qwen/Qwen2.5-7B-Instruct-AWQ` (~6 GB, muat).
  Kuantisasi sedikit menggeser output — pakai hanya jika T4 x2 tak tersedia.

Config dipilih **otomatis di dalam kode** (`experiments/_kaggle_env.py` → `vllm_overrides()`
membaca `torch.cuda.device_count()`), jadi `main()` tetap tanpa argumen dan tak bergantung
pada cell notebook. Ia juga memasang `enforce_eager=True` untuk **melewati torch.compile** —
di T4 yang ketat memori, langkah compile itu sendiri bisa OOM, dan untuk benchmark 18 sampel
percepatannya tak sebanding waktu kompilasi.

Override manual (opsional) lewat env var, menang per-kunci: `GEARTS_VLLM_TP`,
`GEARTS_VLLM_MODEL`, `GEARTS_VLLM_QUANT`, `GEARTS_VLLM_GPU_UTIL`, `GEARTS_VLLM_MAX_LEN`,
`GEARTS_VLLM_DTYPE`. Misal paksa full-precision 2×T4:

```bash
GEARTS_VLLM_TP=2 GEARTS_VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct python experiments/exp1_rq1.py
```

> Catatan: `exp2` memakai 4 setting panjang penalaran dengan model yang sama; adapter
> punya **cache engine** sehingga model dimuat **sekali**, bukan 4×.

## Titik kurva RQ2 (default `exp2_rq2.py`)

`panjang` → `pendek` → `cap-2` → `cap-1` (prompt makin ringkas + batas langkah makin ketat).
Tiap titik mengukur `(mean_tokens, mean_grounding, answer_accuracy)`.
