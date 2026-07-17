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

## RQ1 lintas beberapa model (baseline hallucination lebih kuat)

`run_rq1_multi.py` menjalankan beberapa base model, satu baris per model dalam satu tabel —
menunjukkan halusinasi numerik itu **umum**, bukan khusus satu model. Tiap model jalan di
**proses terpisah** (VRAM dibebaskan antar-model), jadi butuh **GPU besar** (≥ ~24 GB, mis.
A6000). Di kartu 16 GB, pakai `exp1_rq1.py` single-model (AWQ) saja.

```bash
export HF_TOKEN=hf_xxx            # Llama-3.1 & Gemma-2 gated: terima lisensi di HF dulu
python experiments/run_rq1_multi.py
```

Roster default: `Qwen2.5-7B-Instruct` (anchor), `Llama-3.1-8B-Instruct`, `Gemma-2-9B-it`.
Edit `ROSTER` di `experiments/run_rq1_multi.py` untuk ganti/menambah model.

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
membaca jumlah **dan memori** GPU), jadi `main()` tetap tanpa argumen dan tak bergantung
pada cell notebook:

| GPU terdeteksi | Pilihan otomatis |
|---|---|
| 1× besar (≥20 GB: A6000/A100/L4/3090…) | Qwen2.5-7B **presisi penuh**, tanpa AWQ/TP (tercepat & terbersih) |
| 2×T4 | `tensor_parallel_size=2`, presisi penuh dibagi 2 kartu |
| 1×T4 (~16 GB) | model **AWQ 4-bit** |

`dtype=half` dipaksa hanya di kartu pra-Ampere (T4) yang tak punya bf16; kartu besar tetap bf16. Ia juga memasang `enforce_eager=True` untuk **melewati torch.compile** —
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

## RQ3 / RQ4 — metode kami (fine-tuned) vs baseline & ablasi

Butuh **adapter LoRA hasil fine-tune** (F5-02). Jalankan di **GPU besar** (A6000):
LoRA disajikan di atas base **full-precision** `Qwen/Qwen2.5-7B-Instruct` (bukan AWQ),
jadi jangan pakai kartu 16 GB untuk ini. Adapter dilatih di base unsloth 4-bit tetapi
disajikan di base fp16 — ini standar (bobot LoRA low-rank menempel ke modul yang sama).

1. **Taruh adapter** hasil fine-tune (folder berisi `adapter_config.json` +
   `adapter_model.safetensors`) di repo, mis. `notebooks/lora_qwen_penalaran_ts`, atau
   set path-nya:
   ```bash
   export GEARTS_LORA_PATH=/home/jovyan/work/creditaudit/notebooks/lora_qwen_penalaran_ts
   ```
2. **Jalankan (dari root repo):**
   ```bash
   python experiments/exp3_rq3.py   # RQ3 -> experiments/rq3/tabel_rq3.{csv,md}
   python experiments/exp4_rq4.py   # RQ4 -> experiments/rq4/tabel_rq4.{csv,md}
   ```

Base-model dan metode LoRA **berbagi satu engine** (`enable_lora=True`,
`max_lora_rank=32`); LoRA dipilih per-request, jadi 7B dimuat **sekali** saja.

**Metode RQ3** (headline `grounding_per_token`):

| metode | model | bentuk | cerita |
|---|---|---|---|
| B1-prosa | base | prosa bebas | tanpa operasi → grounding ~0 |
| B2-veritime | base | operasi, panjang | tergrounding tapi boros token |
| B3-selfbudget | base | operasi, pendek | murah, grounding turun |
| B4-statistik | — | hitung murni | jawaban saja, tak ada penalaran (0 token) |
| **Kami** | **LoRA** | operasi, terpendek-tergrounding | grounding/token terbaik |

**Ablasi RQ4** (dari Kami, matikan satu komponen): `-finetune` (base),
`-format_operasi` (prosa), `-target_terpendek` (panjang), `-adaptif` (cap-1 tetap).

> **Token RQ3/RQ4 dihitung dari output MENTAH model** (jumlah kata) — adil untuk prosa
> vs operasi — beda dari RQ1/RQ2 yang berbasis langkah terparsing. B4 tak memanggil
> model (0 token; grounding tak berlaku → ditulis `NA`).
>
> Definisi baseline/ablasi ini **default yang langsung bisa dijalankan**; semantik
> finalnya masih boleh dipertajam lewat `/grill-me` (issue F5-03/F5-04).
