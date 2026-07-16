"""Converter train JSONL gearts -> format chat Unsloth/HF (F4-05, keputusan D1).

D1 (CONCERNS): framework fine-tune = Unsloth (QLoRA NF4, Qwen2.5-7B-Instruct).
Butuh train dalam format chat. Converter ini memetakan tiap `Sample` gearts ke
satu percakapan `messages` (role/content):

- system    = instruksi penalar operasi-form (sama dg adapter qwen_vllm._SYSTEM).
- user      = `build_prompt(sample)` (prompt yang IDENTIK dipakai saat inference).
- assistant = reasoning acuan gold, format `LANGKAH n: op = hasil | teks` diakhiri
              `JAWABAN: label` — persis grammar yang di-parse `parse_model_output`,
              jadi round-trip converter->parser mengembalikan langkah+label asli.

Keluaran:
- data/train_unsloth.jsonl   (satu percakapan per baris)
- data/dataset_info.json     (registrasi dataset gaya LLaMA-Factory/Unsloth sharegpt)

Jalankan: python scripts/to_unsloth.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from gearts.adapters.qwen_vllm import _SYSTEM, build_prompt  # noqa: E402
from gearts.schema import Sample, read_jsonl  # noqa: E402

# Sumber train (digabung bila ada): deret NYATA BPS lebih dulu (headline
# data-mining), lalu deret sintetis-terkendali sebagai penyeimbang strata.
# Keduanya 100% grounded + anti-bocor; provenance terlihat dari prefix id
# (`train_bps_*` = real, `train_*` = sintetik) dan didokumentasikan di manifest.
SOURCES = [
    _ROOT / "data" / "synthetic" / "train_real.jsonl",
    _ROOT / "data" / "synthetic" / "train_acuan.jsonl",
]
OUT = _ROOT / "data" / "train_unsloth.jsonl"
INFO = _ROOT / "data" / "dataset_info.json"


def _fmt_hasil(x: float) -> str:
    # buang .0 gaya-int (13.0 -> "13.0" tetap valid _STEP_RE; pakai repr ringkas)
    return f"{x}"


def render_assistant(sample: Sample) -> str:
    """Reasoning gold -> teks target assistant (grammar LANGKAH/JAWABAN)."""
    lines = []
    for s in sample.reasoning:
        teks = f" | {s.teks}" if s.teks else ""
        lines.append(f"LANGKAH {s.langkah}: {s.operasi} = {_fmt_hasil(s.hasil)}{teks}")
    lines.append(f"JAWABAN: {sample.jawaban.label}")
    return "\n".join(lines)


def to_conversation(sample: Sample) -> dict:
    # mode="pendek": instruksi "langkah sesedikit mungkin" selaras dengan target
    # gold = rantai grounded-TERPENDEK (brief v2 4.2). Kalau "panjang", instruksi
    # minta uraian lengkap padahal target minimal -> sinyal latih bertolak belakang.
    return {"messages": [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": build_prompt(sample, mode="pendek")},
        {"role": "assistant", "content": render_assistant(sample)},
    ]}


DATASET_INFO = {
    "gearts_train": {
        "file_name": "train_unsloth.jsonl",
        "formatting": "sharegpt",
        "columns": {"messages": "messages"},
        "tags": {
            "role_tag": "role",
            "content_tag": "content",
            "user_tag": "user",
            "assistant_tag": "assistant",
            "system_tag": "system",
        },
    }
}


def main() -> int:
    present = [p for p in SOURCES if p.exists()]
    if not present:
        print(f"GAGAL: tak ada sumber train {[p.name for p in SOURCES]} "
              f"(jalankan synthesize_train_real.py / synthesize_train_acuan.py dulu).",
              file=sys.stderr)
        return 1
    samples: list[Sample] = []
    counts: dict[str, int] = {}
    for p in present:
        rows = read_jsonl(p)
        counts[p.name] = len(rows)
        samples.extend(rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(to_conversation(s), ensure_ascii=False) + "\n")
    INFO.write_text(json.dumps(DATASET_INFO, ensure_ascii=False, indent=2), encoding="utf-8")
    n_real = sum(1 for s in samples if s.id.startswith("train_bps_"))
    print(f"OK: {len(samples)} percakapan -> {OUT}")
    print(f"    sumber: {counts}")
    print(f"    provenance: {n_real} real (BPS) + {len(samples) - n_real} sintetik-terkendali")
    print(f"    dataset_info -> {INFO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
