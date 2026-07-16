"""Sintesis TRAIN set atas deret **REAL BPS** (F4-03, CONCERNS C5).

Berbeda dari `synthesize_train_acuan.py` (deret sintetis-terkendali), skrip ini
memakai **deret nyata** dari BPS Web API sebagai bahan train — menjawab concern
lomba data-mining bahwa kualitas & pemrosesan data real berbobot. Label reasoning
tetap **disintesis + di-verify** (tak terhindar; itu kontribusi utama): rantai
dibangun `build_reference` yang SAMA dipakai benchmark uji & train sintetik, jadi
definisi grounding identik lintas train/test.

Anti-bocor (§9.4): sumber TEST = World Bank (benchmark_uji). BPS provider **beda**
→ tak berbagi identitas sumber; cek tabrakan numerik lawan benchmark_acuan tetap
dijalankan sebagai bukti tambahan.

Perbedaan penting vs train sintetik — **kesulitan & label MUNCUL dari data**:
tak ada reject-sampling yang memaksa strata seimbang. Untuk tiap deret real
di-generate keempat tugas (TREN/SEGMEN/ANOMALI/PENJELASAN); label + keyakinan
apa adanya hasil `build_reference`. Distribusi nyata dilaporkan di manifest —
ini justru lebih jujur (label tak direkayasa). Untuk ANOMALI, titik dugaan
dipilih otomatis = indeks |z-score| terbesar terhadap seluruh deret (bukan
disuntik), lalu verifier memutuskan ada_anomali / tidak_ada_anomali.

Butuh BPS_API_KEY (env). Key = credential; repo public → JANGAN commit key.
Jalankan: BPS_API_KEY=... python scripts/synthesize_train_real.py
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

from curate_benchmark_uji import ANOMALI, PENJELASAN, SEGMEN, TREN  # noqa: E402
from gearts.schema import Sample, Series, read_jsonl, write_jsonl  # noqa: E402
from gearts.scrapers.bps import series_from_var  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402
from synthesize_reasoning_acuan import ANOMALI_PARAMS, build_reference  # noqa: E402

TASKS = [TREN, SEGMEN, ANOMALI, PENJELASAN]
DIFF_OF_KEYAKINAN = {"tinggi": "easy", "sedang": "medium", "rendah": "hard"}

# Indikator BPS terkurasi — dipilih untuk KERAGAMAN struktur (bukan sekadar banyak):
# tren turun (kemiskinan), naik kuat (garis kemiskinan), stabil (gini), fluktuatif
# (pengangguran). Semua tahunan, per-provinsi (satu deret nyata per provinsi).
# (var_id, domain, freq, satuan override|None, catatan struktur)
VARS = [
    (192, "0000", "tahunan", "persen", "persentase penduduk miskin (P0) — cenderung menurun"),
    (185, "0000", "tahunan", "ribu jiwa", "jumlah penduduk miskin — cenderung menurun"),
    (182, "0000", "tahunan", "rupiah per kapita per bulan", "garis kemiskinan — naik kuat"),
    (543, "0000", "tahunan", "persen", "tingkat pengangguran terbuka — fluktuatif (guncangan COVID)"),
    (98, "0000", "tahunan", None, "gini ratio — relatif stabil"),
]
MIN_LEN = 8            # minimal titik agar tren/segmen/anomali bermakna
MAX_VERVAR = None      # None = semua provinsi; batasi bila ingin memperkecil korelasi


def _register_anomali(sid: str, v: np.ndarray) -> None:
    """Daftarkan titik dugaan anomali secara jujur, non-snooping.

    Pertanyaan tetap per-deret: "apakah pergerakan TERKINI menyimpang dari pola
    yang sudah mapan?". Baseline = jendela awal `nilai[0:b]` (b≈60% deret) yang
    MENGECUALIKAN titik uji, lalu titik dugaan = indeks paling ekstrem di ekor
    `nilai[b:]`. z dihitung verifier thd baseline itu (bukan seluruh deret, agar
    guncangan nyata seperti COVID-2020 tak terdilusi) → ambang |z|>3 memutuskan.
    Deret pendek/baseline datar jatuh ke fallback seluruh deret.
    """
    n = len(v)
    b = max(4, round(n * 0.6))
    if b < n and float(np.std(v[:b])) > 0:
        base = v[:b]
        z = np.abs((v[b:] - float(np.mean(base))) / float(np.std(base)))
        idx = b + int(np.argmax(z))
        ANOMALI_PARAMS[sid] = dict(idx=idx, base=f"nilai[0:{b}]",
                                   peristiwa="pergerakan terkini vs pola awal")
    else:
        mean = float(np.mean(v)) if n else 0.0
        idx = int(np.argmax(np.abs(v - mean))) if n else 0
        ANOMALI_PARAMS[sid] = dict(idx=idx, base=None, peristiwa="titik ekstrem teramati")


def _make_sample(base: Series, konteks: str, var_id: int, vv_slug: str, task: str):
    """Bangun satu Sample (deret real + rantai build_reference) untuk satu tugas.

    Kembalikan (Sample, row) bila 100% grounded & valid; None bila tidak (mis.
    deret degenerate untuk operasi tertentu) → pemanggil melewati.
    """
    sid = f"train_bps_{var_id}_{vv_slug}_{task}"
    v = np.asarray(base.nilai, dtype=float)
    if task == ANOMALI:
        _register_anomali(sid, v)
    stub = Sample(id=sid, series=base, konteks=konteks, pertanyaan="", reasoning=[], jawaban=None)
    try:
        q, reasoning, jawaban, cites = build_reference(stub, task)
    except (ValueError, ZeroDivisionError, IndexError):
        return None
    full = Sample(id=sid, series=base, konteks=konteks, pertanyaan=q,
                  reasoning=reasoning, jawaban=jawaban)
    if verify_sample(full)["grounding_score"] != 100.0 or full.validate():
        return None
    row = dict(id=sid, var=var_id, task=task, difficulty=DIFF_OF_KEYAKINAN[jawaban.keyakinan],
               n=len(base.nilai), n_langkah=len(reasoning),
               chain=" ; ".join(s.operasi for s in reasoning),
               label=jawaban.label, keyakinan=jawaban.keyakinan)
    return full, row


def _vv_slug(nama: str) -> str:
    return nama.split("_")[0][:20]


def generate(key: str | None = None) -> tuple[list[Sample], list[dict], int]:
    """Tarik deret real BPS terkurasi → Sample per (deret × tugas). -> (samples, rows, n_series)."""
    samples: list[Sample] = []
    rows: list[dict] = []
    n_series = 0
    for var_id, domain, freq, satuan, catatan in VARS:
        series = series_from_var(domain, var_id, key=key, freq=freq, satuan=satuan,
                                 max_vervar=MAX_VERVAR, min_len=MIN_LEN)
        for base in series:
            n_series += 1
            vv = _vv_slug(base.nama)
            konteks = (f"{base.nama.replace('_', ' ')} ({base.satuan}), frekuensi {freq}; "
                       f"deret nyata dari BPS (var {var_id}: {catatan}).")
            for task in TASKS:
                made = _make_sample(base, konteks, var_id, vv, task)
                if made is not None:
                    samples.append(made[0])
                    rows.append(made[1])
    return samples, rows, n_series


def check_no_leakage(samples: list[Sample], test_path: Path) -> tuple[int, int]:
    """Cek tabrakan numerik lawan deret uji (benchmark_acuan). -> (n_test, n_tabrakan)."""
    if not test_path.exists():
        return 0, 0
    test_series = [np.asarray(s.series.nilai, dtype=float) for s in read_jsonl(test_path)]
    seen: set[tuple] = set()
    collisions = 0
    for s in samples:
        a = np.asarray(s.series.nilai, dtype=float)
        key = (len(a), round(float(a.sum()), 3))
        if key in seen:
            continue
        seen.add(key)
        for t in test_series:
            if len(a) == len(t) and np.allclose(a, t, atol=1e-6):
                collisions += 1
                break
    return len(test_series), collisions


def render_manifest(rows: list[dict], n_series: int, n_test: int) -> str:
    tasks = Counter(r["task"] for r in rows)
    diffs = Counter(r["difficulty"] for r in rows)
    labels = Counter(r["label"] for r in rows)
    lines = [
        "# Manifest — TRAIN Real BPS (F4-03)",
        "",
        "Train set fine-tune atas **deret nyata BPS** (Badan Pusat Statistik).",
        "Data JSONL: `data/synthetic/train_real.jsonl` (gitignored); regen dengan",
        "`BPS_API_KEY=... python scripts/synthesize_train_real.py`.",
        "",
        f"**Deret real:** {n_series} (per-provinsi, {len(VARS)} indikator BPS).",
        f"**Sampel:** {len(rows)} (deret × tugas yang 100% grounded).",
        "Semua `grounding_score = 100.0` (verifier di dalam loop). Label bersih by",
        "construction; **label & kesulitan MUNCUL dari data** (bukan reject-sampling).",
        "",
        f"**Anti-bocor (§9.4):** sumber test = World Bank; BPS provider beda. "
        f"{n_test} deret uji dibandingkan numerik, **0 tabrakan** (diverifikasi runner).",
        "",
        "## Indikator sumber (BPS)",
        "",
        "| var | freq | catatan struktur |",
        "|---|---|---|",
    ]
    for var_id, _dom, freq, _sat, catatan in VARS:
        lines.append(f"| {var_id} | {freq} | {catatan} |")
    lines += ["", "## Distribusi tugas", "", "| tugas | jumlah |", "|---|---|"]
    for t in TASKS:
        lines.append(f"| {t} | {tasks[t]} |")
    lines += ["", "## Distribusi kesulitan (emergent, dari keyakinan)", "",
              "| kesulitan | jumlah |", "|---|---|"]
    for d in ("easy", "medium", "hard"):
        lines.append(f"| {d} | {diffs[d]} |")
    lines += ["", "## Distribusi label gold", "", "| label | jumlah |", "|---|---|"]
    for lab, c in sorted(labels.items()):
        lines.append(f"| {lab} | {c} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    out = _ROOT / "data" / "synthetic" / "train_real.jsonl"
    manifest = _ROOT / "data" / "manifest_train_real.md"
    test_path = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    samples, rows, n_series = generate()
    if not samples:
        print("GAGAL: 0 sampel (cek BPS_API_KEY / jaringan).", file=sys.stderr)
        return 1
    bad = [s.id for s in samples if verify_sample(s)["grounding_score"] != 100.0]
    if bad:
        print(f"GAGAL: {len(bad)} sampel tidak 100% grounded: {bad[:5]}", file=sys.stderr)
        return 1
    n_test, collisions = check_no_leakage(samples, test_path)
    if collisions:
        print(f"GAGAL: {collisions} deret train bocor dari sumber uji.", file=sys.stderr)
        return 1

    write_jsonl(out, samples)
    manifest.write_text(render_manifest(rows, n_series, n_test), encoding="utf-8")
    tasks = Counter(r["task"] for r in rows)
    diffs = Counter(r["difficulty"] for r in rows)
    print(f"OK: {n_series} deret real BPS -> {len(samples)} sampel (semua 100% grounded) -> {out}")
    print(f"    tugas: {dict(tasks)}")
    print(f"    kesulitan (emergent): {dict(diffs)}")
    print(f"    anti-bocor: {n_test} deret uji dibandingkan, {collisions} tabrakan")
    print(f"    manifest -> {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
