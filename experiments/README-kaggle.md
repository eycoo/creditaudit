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

## Kalau OOM di 1×T4 (16 GB)

Adapter meneruskan `**llm_kwargs` ke `vllm.LLM`. Edit konstruksi adapter di `main()`
(`exp1_rq1.py` / `exp2_rq2.py`) menjadi, misalnya:

```python
QwenVLLMAdapter(mode="panjang", gpu_memory_utilization=0.90, max_model_len=4096, dtype="half")
```

Untuk **2×T4**: tambah `tensor_parallel_size=2`.

## Titik kurva RQ2 (default `exp2_rq2.py`)

`panjang` → `pendek` → `cap-2` → `cap-1` (prompt makin ringkas + batas langkah makin ketat).
Tiap titik mengukur `(mean_tokens, mean_grounding, answer_accuracy)`.
