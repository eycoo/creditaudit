"""Generate paper figures from the REAL experiment CSVs (F6-04).

Reads experiments/rq1/tabel_rq1.csv and experiments/rq2/kurva_rq2.csv and writes
two black-and-white-safe PNGs into paper/:

  paper/plot_rq1.png  — akurasi vs grounding per base model (RQ1)
  paper/plot_rq2.png  — grounding & akurasi vs jumlah token (RQ2 trade-off)

B/W-safe: grayscale fills, distinct hatches/markers/linestyles, black edges,
no reliance on color, >=300 dpi (GEMASTIK print assumption). Pure visualization
of real numbers — no fabricated data.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.linewidth": 0.7,
    "axes.grid": True,
    "grid.linewidth": 0.4,
    "grid.alpha": 0.5,
})

MODEL_LABEL = {"qwen2.5-7b": "Qwen2.5-7B", "llama-3.1-8b": "Llama-3.1-8B", "gemma-2-9b": "Gemma-2-9B"}
ORDER = ["qwen2.5-7b", "llama-3.1-8b", "gemma-2-9b"]


def _read(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def plot_rq1() -> None:
    rows = {r["model"]: r for r in _read(ROOT / "experiments" / "rq1" / "tabel_rq1.csv")}
    models = [m for m in ORDER if m in rows]
    acc = [float(rows[m]["answer_accuracy"]) for m in models]
    grd = [float(rows[m]["mean_grounding"]) for m in models]

    fig, ax = plt.subplots(figsize=(3.3, 2.3))
    x = range(len(models))
    w = 0.38
    ax.bar([i - w / 2 for i in x], acc, w, label="Akurasi jawaban",
           color="0.35", edgecolor="black", linewidth=0.6)
    ax.bar([i + w / 2 for i in x], grd, w, label="Skor grounding",
           color="0.80", edgecolor="black", linewidth=0.6, hatch="////")
    for i, v in zip(x, acc):
        ax.text(i - w / 2, v + 1.5, f"{v:.0f}", ha="center", va="bottom", fontsize=6.5)
    for i, v in zip(x, grd):
        ax.text(i + w / 2, v + 1.5, f"{v:.1f}", ha="center", va="bottom", fontsize=6.5)
    ax.set_xticks(list(x))
    ax.set_xticklabels([MODEL_LABEL[m] for m in models], fontsize=7)
    ax.set_ylabel("Persen (%)")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "plot_rq1.png", dpi=320)
    plt.close(fig)


def plot_rq2() -> None:
    rows = _read(ROOT / "experiments" / "rq2" / "kurva_rq2.csv")
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)
    for m in by_model:
        by_model[m].sort(key=lambda r: float(r["mean_tokens"]))

    styles = {
        "qwen2.5-7b": dict(marker="o", linestyle="-", color="0.0"),
        "llama-3.1-8b": dict(marker="s", linestyle="--", color="0.45"),
        "gemma-2-9b": dict(marker="^", linestyle="-.", color="0.0"),
    }

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.3, 2.95), sharex=True,
                                   layout="constrained")
    for m in ORDER:
        if m not in by_model:
            continue
        pts = by_model[m]
        tok = [float(p["mean_tokens"]) for p in pts]
        grd = [float(p["mean_grounding"]) for p in pts]
        acc = [float(p["answer_accuracy"]) for p in pts]
        st = styles[m]
        ax1.plot(tok, grd, label=MODEL_LABEL[m], markersize=4, linewidth=1.0,
                 markerfacecolor="white", markeredgewidth=0.8, **st)
        ax2.plot(tok, acc, markersize=4, linewidth=1.0,
                 markerfacecolor="white", markeredgewidth=0.8, **st)

    ax1.set_ylabel("Skor grounding (%)")
    ax1.set_ylim(-2, 22)
    ax1.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
    ax2.set_ylabel("Akurasi jawaban (%)")
    ax2.set_ylim(0, 100)
    ax2.set_xlabel("Rata-rata jumlah token penalaran")
    fig.savefig(OUT / "plot_rq2.png", dpi=320)
    plt.close(fig)


if __name__ == "__main__":
    plot_rq1()
    plot_rq2()
    print("wrote", OUT / "plot_rq1.png")
    print("wrote", OUT / "plot_rq2.png")
