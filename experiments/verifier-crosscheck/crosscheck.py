"""Cross-check INDEPENDEN verifier — C3 / #5.

Membantah tuduhan sirkular ("skor grounding = apa kata kodemu sendiri"): tiap
langkah ter-skor di `benchmark_acuan.jsonl` + `benchmark_uji.jsonl` dihitung ulang
lewat JALUR KEDUA (`independent.py`, NumPy murni, tanpa `gearts`), lalu dicocokkan
dengan `expected` dari `gearts.verifier.verify_sample`. Kalau dua jalur independen
setuju 100%, `expected` verifier bukan artefak satu implementasi.

Keluaran:
  * tabel per-file + total (langkah ter-skor, match, mismatch, match%),
  * tiap mismatch di-dump (id, operasi, nilai-verifier, nilai-independen) = bug verifier,
  * `spotcheck.csv` (10 grounded + 10 ungrounded) untuk audit manusia.

Deterministik, tanpa LLM judge. Jalankan dari root repo:
    python experiments/verifier-crosscheck/crosscheck.py
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # independent.py

import independent  # noqa: E402  (jalur kedua — NumPy murni)
from gearts.schema import Sample  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402

# Sumber ber-reasoning yang di-cross-check. `train_acuan.jsonl` (sintetik) adalah
# data yang justru DIBERSIHKAN verifier — inti concern C3 ("bersihin train"), jadi
# ikut di-cross-check. `benchmark_uji.jsonl` = set uji telanjang (reasoning kosong,
# diisi model saat eval), otomatis 0 langkah ter-skor — dibiarkan agar eksplisit.
BENCHMARKS = [
    _ROOT / "data" / "processed" / "benchmark_acuan.jsonl",
    _ROOT / "data" / "processed" / "benchmark_uji.jsonl",
    _ROOT / "data" / "synthetic" / "train_acuan.jsonl",
]
SPOTCHECK_CSV = Path(__file__).resolve().parent / "spotcheck.csv"
_EPS = 1e-6  # dua jalur deterministik & rumus setara -> harus ~identik


def _read_lines(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _expected_match(ve, ie) -> bool:
    """Cocokkan expected verifier (ve) vs independen (ie)."""
    if ve is None or ie is None:
        return ve is None and ie is None  # dua-duanya ungroundable = sepakat
    if isinstance(ve, list) or isinstance(ie, list):  # set-valued
        return sorted(_as_int_list(ve)) == sorted(_as_int_list(ie))
    return abs(float(ve) - float(ie)) <= max(_EPS, _EPS * abs(float(ve)))


def _as_int_list(x):
    if isinstance(x, (list, tuple, set)):
        return [int(i) for i in x]
    return [int(x)]


def _series_ringkas(nilai: list[float], k: int = 6) -> str:
    head = ", ".join(f"{v:g}" for v in nilai[:k])
    return f"[{head}{', …' if len(nilai) > k else ''}] (n={len(nilai)})"


def crosscheck_file(path: dict) -> tuple[list[dict], list[dict]]:
    """Return (rows_per_scored_step, mismatches) untuk satu file benchmark."""
    rows: list[dict] = []
    mism: list[dict] = []
    for sdict in _read_lines(path):
        v_report = verify_sample(Sample.from_dict(sdict))
        i_steps = independent.recompute_sample(sdict)
        i_by_langkah = {s["langkah"]: s for s in i_steps}
        for vstep in v_report["steps"]:
            if vstep.get("grounded") is None:
                continue  # langkah non-skalar tak ter-skor -> lewati
            istep = i_by_langkah[vstep["langkah"]]
            ve, ie = vstep.get("expected"), istep.get("expected")
            ok = _expected_match(ve, ie)
            row = {
                "id": sdict["id"], "langkah": vstep["langkah"],
                "operasi": next(s["operasi"] for s in sdict["reasoning"]
                                if s["langkah"] == vstep["langkah"]),
                "series": _series_ringkas(sdict["series"]["nilai"]),
                "claimed": vstep["claimed"],
                "verifier_expected": ve, "independen_expected": ie,
                "verifier_grounded": vstep["grounded"],
                "match": ok,
            }
            rows.append(row)
            if not ok:
                mism.append(row)
    return rows, mism


def _fmt_pct(match: int, total: int) -> str:
    return f"{100.0 * match / total:.2f}%" if total else "n/a"


def _print_table(per_file: dict[str, list[dict]]) -> None:
    print("\n=== Cross-check independen: verifier vs jalur kedua (NumPy murni) ===")
    print(f"{'file':<26}{'langkah':>9}{'match':>8}{'mismatch':>10}{'match%':>10}")
    tot = tot_m = 0
    for name, rows in per_file.items():
        m = sum(r["match"] for r in rows)
        tot += len(rows)
        tot_m += m
        print(f"{name:<26}{len(rows):>9}{m:>8}{len(rows) - m:>10}{_fmt_pct(m, len(rows)):>10}")
    print("-" * 63)
    print(f"{'TOTAL':<26}{tot:>9}{tot_m:>8}{tot - tot_m:>10}{_fmt_pct(tot_m, tot):>10}")
    return tot, tot_m


def _dump_mismatches(mism: list[dict]) -> None:
    if not mism:
        print("\nTak ada mismatch — dua jalur sepakat penuh. Verifier tak sirkular pada set ini.")
        return
    print(f"\n!!! {len(mism)} MISMATCH (dugaan bug verifier) — dump:")
    for r in mism:
        print(f"  id={r['id']} langkah={r['langkah']} operasi={r['operasi']}")
        print(f"     verifier={r['verifier_expected']}  independen={r['independen_expected']}")


def _write_spotcheck(all_rows: list[dict], seed: int = 20260716, k: int = 10) -> None:
    """10 grounded + 10 ungrounded untuk audit manusia -> spotcheck.csv.

    Benchmark = verifier-clean (semua langkah grounded), jadi kelas 'ungrounded'
    alami kosong. Untuk memberi auditor kedua kelas, baris ungrounded dibuat lewat
    PERTURBASI deterministik (klaim dirusak sampai keluar toleransi) dan ditandai
    `sumber=perturbasi`. Baris grounded diambil apa adanya (`sumber=benchmark`).
    """
    import csv

    rng = random.Random(seed)
    grounded_pool = [r for r in all_rows if r["verifier_grounded"]]
    natural_ung = [r for r in all_rows if not r["verifier_grounded"]]

    grounded = rng.sample(grounded_pool, min(k, len(grounded_pool)))
    out_rows = [_spot_row(r, "benchmark", r["claimed"], True) for r in grounded]

    # ungrounded: pakai yang alami dulu, sisanya perturbasi
    ung_src = list(natural_ung)
    rng.shuffle(ung_src)
    for r in ung_src[:k]:
        out_rows.append(_spot_row(r, "benchmark", r["claimed"], False))
    need = k - min(k, len(natural_ung))
    if need > 0:
        cand = rng.sample([r for r in grounded_pool if isinstance(r["verifier_expected"], (int, float))],
                          min(need, len(grounded_pool)))
        for r in cand:
            base = float(r["verifier_expected"])
            bad = base + max(1.0, abs(base)) * 0.5 + 5.0  # jauh > toleransi 1%
            out_rows.append(_spot_row(r, "perturbasi", bad, False))

    cols = ["id", "langkah", "operasi", "series", "claimed_audit",
            "verifier_expected", "independen_expected", "verifier_grounded",
            "kelas", "sumber", "cocok_menurut_auditor"]
    with open(SPOTCHECK_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nspotcheck.csv ditulis: {SPOTCHECK_CSV} "
          f"({sum(r['kelas'] == 'grounded' for r in out_rows)} grounded + "
          f"{sum(r['kelas'] == 'ungrounded' for r in out_rows)} ungrounded)")


def _spot_row(r: dict, sumber: str, claimed_audit, grounded: bool) -> dict:
    return {
        "id": r["id"], "langkah": r["langkah"], "operasi": r["operasi"],
        "series": r["series"], "claimed_audit": claimed_audit,
        "verifier_expected": r["verifier_expected"],
        "independen_expected": r["independen_expected"],
        "verifier_grounded": grounded,
        "kelas": "grounded" if grounded else "ungrounded",
        "sumber": sumber,
        "cocok_menurut_auditor": "",  # diisi manusia: ya/tidak
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-check independen verifier (C3/#5)")
    ap.add_argument("--no-spotcheck", action="store_true", help="lewati tulis spotcheck.csv")
    args = ap.parse_args()

    per_file: dict[str, list[dict]] = {}
    all_rows: list[dict] = []
    all_mism: list[dict] = []
    for path in BENCHMARKS:
        if not path.exists():
            print(f"(lewati) {path.name} tak ada di worktree ini.")
            continue
        rows, mism = crosscheck_file(path)
        per_file[path.name] = rows
        all_rows.extend(rows)
        all_mism.extend(mism)

    if not all_rows:
        print("Tak ada benchmark ditemukan. Pastikan data/processed/*.jsonl ada.")
        return 1

    tot, tot_m = _print_table(per_file)
    _dump_mismatches(all_mism)
    if not args.no_spotcheck:
        _write_spotcheck(all_rows)

    print(f"\nRINGKAS: match {tot_m}/{tot} = {_fmt_pct(tot_m, tot)} "
          f"(target 100%). Mismatch: {len(all_mism)}.")
    return 1 if all_mism else 0


if __name__ == "__main__":
    raise SystemExit(main())
