"""RQ1 across several base models — one row per model in a single table.

Baseline hallucination (RQ1) is far more convincing measured on more than one
model: it shows unauditable numeric reasoning is a *general* LLM trait, not a
Qwen quirk (brief v2 §5). The literature's own TS-reasoning benchmarks compare a
spread of models the same way (e.g. MTBench: GPT-4o / Claude / Gemini / Llama-3.1).

Each model runs in its **own subprocess** (`exp1_rq1.py` with `GEARTS_MODEL_ID`),
so vLLM fully frees the GPU between models — three 7-9B models never coexist in
VRAM. Every worker drops a one-row JSON; this script then writes the combined
`experiments/rq1/tabel_rq1.{csv,md}`.

Roster is full-precision, sized for a big GPU (≥ ~24 GB, e.g. A6000 48 GB). On a
16 GB card run the single-model `exp1_rq1.py` (AWQ) instead.

    python experiments/run_rq1_multi.py

Note: Llama-3.1 and Gemma-2 are **gated** on Hugging Face — accept their licenses
on the model page and `export HF_TOKEN=...` first, or swap them in ROSTER below.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "experiments"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _report import write_csv, write_markdown_table  # noqa: E402

# (row label, HF model id). Edit freely; each entry is one RQ1 row.
ROSTER = [
    ("qwen2.5-7b", "Qwen/Qwen2.5-7B-Instruct"),   # fine-tune anchor
    ("llama-3.1-8b", "meta-llama/Llama-3.1-8B-Instruct"),  # gated (MTBench-aligned)
    ("gemma-2-9b", "google/gemma-2-9b-it"),        # gated (third family)
]

COLUMNS = ["model", "n", "answer_accuracy", "mean_grounding", "mean_tokens"]
OUTDIR = _ROOT / "experiments" / "rq1"
EXP1 = _ROOT / "experiments" / "exp1_rq1.py"


def main() -> int:  # pragma: no cover - needs GPU/vLLM + subprocess
    rowsdir = OUTDIR / "rows"
    rowsdir.mkdir(parents=True, exist_ok=True)

    for slug, model_id in ROSTER:
        row_path = rowsdir / f"{slug}.json"
        env = {
            **os.environ,
            "GEARTS_MODEL_ID": model_id,
            "GEARTS_MODEL_NAME": slug,
            "GEARTS_ROW_OUT": str(row_path),
        }
        print(f"\n=== RQ1: {slug} ({model_id}) ===", flush=True)
        r = subprocess.run([sys.executable, str(EXP1)], env=env)
        if r.returncode != 0:
            print(f"!! {slug} GAGAL (returncode {r.returncode}) — dilewati", file=sys.stderr)

    rows = [json.loads((rowsdir / f"{slug}.json").read_text(encoding="utf-8"))
            for slug, _ in ROSTER if (rowsdir / f"{slug}.json").exists()]
    if not rows:
        print("Tak ada model yang berhasil.", file=sys.stderr)
        return 1

    write_csv(OUTDIR / "tabel_rq1.csv", rows, COLUMNS)
    write_markdown_table(OUTDIR / "tabel_rq1.md", rows, COLUMNS,
                         "RQ1 — akurasi vs grounding (tanpa fine-tune), lintas model")
    print(f"\nGabungan {len(rows)} model -> {OUTDIR / 'tabel_rq1.md'}")
    for r in rows:
        print(r)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
