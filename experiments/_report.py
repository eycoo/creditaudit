"""Shared reporting helpers for the Fase-3 experiments (RQ1/RQ2).

Deterministic writers so exp1/exp2 emit a stable, F6-04-consumable layout: a CSV
(machine-readable) plus a Markdown table (paste-ready). No model or GPU here.
"""
from __future__ import annotations

import csv
from pathlib import Path

from gearts.schema import Sample, read_jsonl

BENCHMARK_DEFAULT = Path("data/processed/benchmark_acuan.jsonl")


def load_benchmark(path: str | Path = BENCHMARK_DEFAULT) -> list[Sample]:
    """Load the acuan benchmark JSONL (regenerate via scripts/synthesize_reasoning_acuan.py)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} tak ada. Regenerasi: `python scripts/synthesize_reasoning_acuan.py` "
            "(butuh data/processed/benchmark_uji.jsonl dari F2-01)."
        )
    return read_jsonl(path)


def _fmt(v) -> str:
    return f"{v:.2f}" if isinstance(v, float) else str(v)


def write_csv(path: str | Path, rows: list[dict], columns: list[str]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})
    return path


def write_markdown_table(path: str | Path, rows: list[dict], columns: list[str], title: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "| " + " | ".join(columns) + " |",
             "|" + "|".join("---" for _ in columns) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(_fmt(r.get(c, "")) for c in columns) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
