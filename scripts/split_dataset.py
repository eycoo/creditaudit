"""Split train/test + stratifikasi + cek anti-bocor (F4-05, brief 9.4).

Split sudah terwujud sebagai DUA file terpisah (bukan repartition satu pool):
- TRAIN = data/synthetic/train_acuan.jsonl   -> semi-sintetik (F4-04), 336 sampel.
- TEST  = data/processed/benchmark_acuan.jsonl -> deret REAL World Bank (F2-02), 18 sampel.
  (benchmark_uji.jsonl = deret yang sama tanpa reasoning; acuan dipakai karena
   ter-commit & membawa series identik.)

Tugas skrip: stratifikasi (tugas x kesulitan) tiap sisi + cek anti-bocor
(brief 9.4: "sumber pada uji tidak muncul pada latih"), lalu tulis manifest.
Seed tetap (data F4-04 deterministik) -> reprodusibel.

Jalankan: python scripts/split_dataset.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from gearts.schema import read_jsonl  # noqa: E402
from synthesize_reasoning_acuan import DIFF_OF, TASK_OF  # noqa: E402

TRAIN = _ROOT / "data" / "synthetic" / "train_acuan.jsonl"
TEST = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"
MANIFEST = _ROOT / "data" / "manifest_split.md"

TASKS = ["tren", "segmen", "anomali", "penjelasan"]
DIFFS = ["easy", "medium", "hard"]


def _train_task_diff(sid: str) -> tuple[str, str]:
    # id train: train_<task>_<diff>_<rep>
    _, task, diff, _ = sid.split("_", 3)
    return task, diff


def _test_task_diff(sid: str) -> tuple[str, str]:
    return TASK_OF[sid], DIFF_OF[sid]


def _strata(items, keyfn) -> Counter:
    return Counter(keyfn(s.id) for s in items)


def check_leakage(train, test) -> dict:
    """Anti-bocor brief 9.4. -> laporan dict; `ok` True bila tak ada kebocoran.

    Tiga sumbu:
    - namespace id: train `train_*` vs test `uji_*` harus disjoint.
    - identitas numerik deret: tak ada deret train == deret test (allclose).
    - sumber: train sintetik-terkendali vs test World Bank real (beda by construction).
    Overlap NAMA indikator dilaporkan sebagai catatan optik (bukan bocor: deret
    numeriknya beda & sumbernya beda), agar jujur.
    """
    train_ids = {s.id for s in train}
    test_ids = {s.id for s in test}
    id_overlap = train_ids & test_ids

    test_series = [(s.id, np.asarray(s.series.nilai, dtype=float)) for s in test]
    numeric_collisions = []
    for s in train:
        a = np.asarray(s.series.nilai, dtype=float)
        for tid, t in test_series:
            if len(a) == len(t) and np.allclose(a, t, atol=1e-6):
                numeric_collisions.append((s.id, tid))
                break

    train_names = {s.series.nama for s in train}
    test_names = {s.series.nama for s in test}
    name_overlap = sorted(train_names & test_names)

    ok = not id_overlap and not numeric_collisions
    return dict(ok=ok, id_overlap=sorted(id_overlap),
                numeric_collisions=numeric_collisions, name_overlap=name_overlap,
                n_train=len(train), n_test=len(test))


def _strata_table(title, counter, tasks, diffs) -> list[str]:
    lines = [f"### {title}", "",
             "| tugas \\ kesulitan | " + " | ".join(diffs) + " | total |",
             "|---" * (len(diffs) + 2) + "|"]
    for t in tasks:
        row = [counter[(t, d)] for d in diffs]
        lines.append(f"| {t} | " + " | ".join(str(x) for x in row) + f" | {sum(row)} |")
    tot = [sum(counter[(t, d)] for t in tasks) for d in diffs]
    lines.append("| **total** | " + " | ".join(str(x) for x in tot) + f" | {sum(tot)} |")
    lines.append("")
    return lines


def render_manifest(train, test, leak) -> str:
    tr = Counter(_train_task_diff(s.id) for s in train)
    te = Counter(_test_task_diff(s.id) for s in test)
    lines = [
        "# Manifest — Split Train/Test (F4-05)",
        "",
        "Split brief 9.4: **train** semi-sintetik untuk skala, **test** deret asli",
        "untuk generalisasi; distratifikasi tugas x kesulitan; sumber uji tak muncul",
        "di train. Seed tetap (F4-04 deterministik) -> reprodusibel.",
        "",
        f"- **TRAIN** `data/synthetic/train_acuan.jsonl` — {leak['n_train']} sampel, "
        "sintetis-terkendali (ADR-0004).",
        f"- **TEST** `data/processed/benchmark_acuan.jsonl` — {leak['n_test']} sampel, "
        "deret REAL World Bank (F2-01/02).",
        "",
        "## Anti-bocor (brief 9.4)",
        "",
        f"- namespace id disjoint (`train_*` vs `uji_*`): "
        f"{'LOLOS' if not leak['id_overlap'] else 'GAGAL ' + str(leak['id_overlap'])}.",
        f"- identitas numerik deret (train vs {leak['n_test']} deret uji): "
        f"**{len(leak['numeric_collisions'])} tabrakan** "
        f"-> {'LOLOS' if not leak['numeric_collisions'] else 'GAGAL'}.",
        "- sumber beda by construction: train sintetik-terkendali; test World Bank "
        "(tahunan makro). Tak ada sumber uji dipakai di train.",
        (f"- nama indikator: {len(leak['name_overlap'])} sama "
         f"({', '.join(leak['name_overlap'])}) — bukan bocor (deret numerik & sumber beda), "
         "tapi dihindari untuk optik."
         if leak["name_overlap"] else
         "- nama indikator train **disjoint** dari 18 nama uji (0 tumpang-tindih)."),
        "",
        f"**Status anti-bocor: {'LOLOS' if leak['ok'] else 'GAGAL'}.**",
        "",
        "## Distribusi (tugas x kesulitan)",
        "",
    ]
    lines += _strata_table("TRAIN", tr, TASKS, DIFFS)
    lines += _strata_table("TEST", te, TASKS, DIFFS)
    return "\n".join(lines)


def main() -> int:
    if not TRAIN.exists():
        print(f"GAGAL: {TRAIN} tak ada (jalankan F4-04 dulu).", file=sys.stderr)
        return 1
    if not TEST.exists():
        print(f"GAGAL: {TEST} tak ada (jalankan F2-02 dulu).", file=sys.stderr)
        return 1
    train, test = read_jsonl(TRAIN), read_jsonl(TEST)
    leak = check_leakage(train, test)
    MANIFEST.write_text(render_manifest(train, test, leak), encoding="utf-8")
    print(f"TRAIN {leak['n_train']} | TEST {leak['n_test']}")
    print(f"anti-bocor: id_overlap={leak['id_overlap'] or 0}, "
          f"numeric_collisions={len(leak['numeric_collisions'])}, "
          f"name_overlap={leak['name_overlap'] or 0}")
    print(f"status: {'LOLOS' if leak['ok'] else 'GAGAL'}; manifest -> {MANIFEST}")
    return 0 if leak["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
