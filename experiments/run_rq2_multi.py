"""RQ2 across the model roster — grounding-vs-token curve per model.

Same idea as run_rq1_multi.py, for the RQ2 curve: showing grounding falls faster
than accuracy as reasoning shortens is more convincing across several base models
(the tradeoff is general, not Qwen-specific). Each model runs in its **own
subprocess** (exp2_rq2.py with GEARTS_MODEL_ID); within that process the four
length settings share one loaded engine (adapter cache), so a model is loaded
once and no two models sit in VRAM together. Every worker drops its four tagged
curve rows; this script merges them into experiments/rq2/kurva_rq2.{csv,md} with
a `model` column (rows grouped model × setting).

Full precision — needs a big GPU (≥ ~24 GB, e.g. A6000). Roster is shared with
run_rq1_multi.py (edit ROSTER there).

    python experiments/run_rq2_multi.py

Llama-3.1 & Gemma-2 are gated on HF — set HF_TOKEN or swap them in ROSTER.
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
from run_rq1_multi import ROSTER  # noqa: E402  (single source of truth for the model set)

COLUMNS = ["model", "setting", "mean_tokens", "mean_grounding", "answer_accuracy", "n"]
OUTDIR = _ROOT / "experiments" / "rq2"
EXP2 = _ROOT / "experiments" / "exp2_rq2.py"


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
        print(f"\n=== RQ2: {slug} ({model_id}) ===", flush=True)
        r = subprocess.run([sys.executable, str(EXP2)], env=env)
        if r.returncode != 0:
            print(f"!! {slug} GAGAL (returncode {r.returncode}) — dilewati", file=sys.stderr)

    rows: list[dict] = []
    for slug, _ in ROSTER:
        f = rowsdir / f"{slug}.json"
        if f.exists():
            rows.extend(json.loads(f.read_text(encoding="utf-8")))  # 4 curve rows per model
    if not rows:
        print("Tak ada model yang berhasil.", file=sys.stderr)
        return 1

    write_csv(OUTDIR / "kurva_rq2.csv", rows, COLUMNS)
    write_markdown_table(OUTDIR / "kurva_rq2.md", rows, COLUMNS,
                         "RQ2 — grounding & akurasi vs panjang penalaran, lintas model")
    print(f"\nGabungan {len(rows)} baris (model×setting) -> {OUTDIR / 'kurva_rq2.md'}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
