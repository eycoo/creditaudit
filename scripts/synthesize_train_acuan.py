"""Sintesis TRAIN set acuan F4-04 — deret sintetis-terkendali + rantai operasi
TERPENDEK yang tiap angkanya lolos verifier (grounding 100% by construction),
distratifikasi tugas x kesulitan, skala ratusan item.

Kenapa sintetis-terkendali, bukan scrape/WB (ADR-0004):
- F4-03 (scrape penuh) ditunda; brief v2 4.3 memang membolehkan train "didominasi
  semi-sintetis (deret nyata atau TERKENDALI + reasoning terverifikasi)".
- 18 deret WB di `data/raw/` justru SUMBER TEST (benchmark_uji). Anti-bocor 9.4
  melarang sumber test muncul di train, jadi deret WB itu TIDAK dipakai di sini —
  train dibangkitkan sendiri, sepenuhnya lepas dari sumber uji.
- Deret terkendali memberi kendali penuh atas strata (tugas x kesulitan) dan
  skala, sambil tetap 100% grounded lewat verifier di dalam loop.

Verifier IN THE LOOP (label bersih by construction, brief v2 4.3 langkah 4-5):
tiap sampel dibangun -> `hasil` tiap langkah dihitung ULANG oleh verifier
(`eval_step`) -> `verify_sample` di-assert 100%. Sampel yang tak 100% grounded
(mis. std baseline 0, base persen_naik 0) DIBUANG dan dibangkitkan ulang dengan
seed berikut (drop/retry), sehingga keluaran akhir bersih.

Semantik operasi & label mengikuti ADR-0003 + F2-02: rantai dibangun lewat
`build_reference` yang sama dipakai benchmark acuan, jadi train dan test memakai
definisi grounding yang identik. Untuk ANOMALI parameter (idx titik + jendela
baseline) diketahui saat pembangkitan deret lalu didaftarkan ke `ANOMALI_PARAMS`.

Kesulitan menentukan sinyal (bukan sekadar label), sesuai brief v2 4.2:
- easy   : sinyal jelas  -> label tegas, keyakinan tinggi.
- medium : sinyal sedang -> label tegas, keyakinan sedang.
- hard   : ambigu/menjebak -> relatif_stabil / setara / tidak_ada_anomali (near-miss)
           / tidak_monoton. Melatih model menahan diri, bukan asal klaim.

Jalankan: python scripts/synthesize_train_acuan.py
"""
from __future__ import annotations

import sys
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from curate_benchmark_uji import ANOMALI, PENJELASAN, SEGMEN, TREN  # noqa: E402
from gearts.schema import Sample, Series, read_jsonl, write_jsonl  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402
from synthesize_reasoning_acuan import ANOMALI_PARAMS, build_reference  # noqa: E402

TASKS = [TREN, SEGMEN, ANOMALI, PENJELASAN]
DIFFS = ["easy", "medium", "hard"]
PER_STRATUM = 28          # 4 tugas x 3 kesulitan x 28 = 336 (> target 300)
ROUND = 2                 # desimal nilai deret; hasil dihitung DARI deret ini
MAX_ATTEMPTS = 400        # reject-sampling: buang deret yang tak lolos band/grounding

# Profil domain (deret sintetis diberi rasa domain Indonesia yang masuk akal).
# (nama, domain, satuan, freq, (level_min, level_max)). Level jadi skala deret;
# bentuk per-tugas ditumpangkan di atasnya. Semua level positif (aman untuk
# persen_naik base != 0).
# Nama SENGAJA disjoint dari 18 nama indikator benchmark uji (anti-bocor 9.4:
# tak berbagi identitas sumber dengan test).
PROFILES = [
    ("cakupan_posyandu", "kesehatan", "persen balita", "tahunan", (70.0, 95.0)),
    ("kasus_demam_berdarah", "kesehatan", "kasus per minggu", "mingguan", (60.0, 400.0)),
    ("harga_beras", "pangan-pertanian", "rupiah per kg", "mingguan", (10000.0, 15000.0)),
    ("stok_beras_bulog", "pangan-pertanian", "ribu ton", "tahunan", (90.0, 130.0)),
    ("beban_listrik", "energi", "MW", "harian", (15000.0, 25000.0)),
    ("suhu_udara", "cuaca", "derajat celsius", "harian", (24.0, 33.0)),
    ("peserta_jkn", "kesehatan", "persen penduduk", "tahunan", (63.0, 72.0)),
    ("inflasi_inti", "pangan-pertanian", "persen", "tahunan", (3.0, 9.0)),
]


def _seed(*parts) -> int:
    return zlib.crc32("|".join(str(p) for p in parts).encode()) & 0xFFFFFFFF


def _round(a: np.ndarray) -> list[float]:
    return [round(float(x), ROUND) for x in a]


# --- pembangkit deret per tugas: bentuk mengikuti kesulitan -------------------

def _gen_tren(diff: str, rng: np.random.Generator, L: float, n: int) -> np.ndarray:
    # frac = |slope*(n-1)| / |mean| menentukan label (lihat build_reference TREN).
    band = {"easy": (0.35, 0.90), "medium": (0.08, 0.28), "hard": (0.0, 0.03)}[diff]
    frac = rng.uniform(*band)
    sign = rng.choice([-1.0, 1.0])
    slope = sign * frac * L / (n - 1)
    x = np.arange(n)
    noise = rng.normal(0.0, 0.02 * L, n)
    return L + slope * x + noise


def _gen_segmen(diff: str, rng: np.random.Generator, L: float, n: int) -> np.ndarray:
    # frac = |mean(akhir)-mean(awal)| / |mean(awal)|.
    band = {"easy": (0.35, 0.90), "medium": (0.08, 0.28), "hard": (0.0, 0.03)}[diff]
    h = n // 2
    delta = rng.choice([-1.0, 1.0]) * rng.uniform(*band) * L
    first = L + rng.normal(0.0, 0.02 * L, h)
    second = L + delta + rng.normal(0.0, 0.02 * L, n - h)
    return np.concatenate([first, second])


def _gen_anomali(diff: str, rng: np.random.Generator, L: float, n: int):
    # Deret stasioner di sekitar L; satu titik disuntik pada `idx` sebesar
    # +/-k*sd. z verifier = (x-mean(base))/std(base) ~ k. Jendela baseline
    # eksplisit (ADR-0003 Item 3C) mengecualikan titik anomali.
    # |z|: easy >=5, medium [3,5), hard [1.6,2.8) -> tidak_ada_anomali (near-miss).
    kband = {"easy": (5.0, 8.0), "medium": (3.3, 4.6), "hard": (1.6, 2.7)}[diff]
    sd = 0.04 * L
    v = L + rng.normal(0.0, sd, n)
    b0 = 1
    blen = int(rng.integers(6, 11))
    b1 = b0 + blen
    idx = int(rng.integers(b1 + 1, n))
    k = rng.uniform(*kband)
    v[idx] = L + rng.choice([-1.0, 1.0]) * k * sd
    return v, idx, b0, b1


def _gen_penjelasan(diff: str, rng: np.random.Generator, L: float, n: int) -> np.ndarray:
    # Label komposit: arah (slope) + besaran (persen_naik ujung-ke-ujung).
    if diff in ("easy", "medium"):
        pband = {"easy": (0.25, 0.80), "medium": (0.06, 0.18)}[diff]
        pct = rng.choice([-1.0, 1.0]) * rng.uniform(*pband)
        body = np.linspace(L, L * (1.0 + pct), n) + rng.normal(0.0, 0.004 * L, n)
        return body
    # hard: tidak_monoton -> tanda slope != tanda persen ujung-ke-ujung.
    if rng.integers(2) == 0:  # naik hampir sepanjang deret, jatuh di ujung (slope>0, pct<0)
        peak = L * (1.0 + rng.uniform(0.30, 0.70))
        body = np.linspace(L, peak, n - 1) + rng.normal(0.0, 0.004 * L, n - 1)
        end = L * (1.0 - rng.uniform(0.05, 0.20))
    else:                     # turun hampir sepanjang deret, melonjak di ujung (slope<0, pct>0)
        trough = L * (1.0 - rng.uniform(0.25, 0.50))
        body = np.linspace(L, trough, n - 1) + rng.normal(0.0, 0.004 * L, n - 1)
        end = L * (1.0 + rng.uniform(0.05, 0.20))
    return np.concatenate([body, [end]])


# --- prasyarat penerimaan: (label, keyakinan) cocok maksud kesulitan ----------

def _accept(task: str, diff: str, label: str, keyakinan: str) -> bool:
    if task == TREN:
        if diff == "hard":
            return label == "relatif_stabil"
        return label in {"meningkat", "menurun"} and keyakinan == ("tinggi" if diff == "easy" else "sedang")
    if task == SEGMEN:
        if diff == "hard":
            return label == "setara"
        moved = {"paruh_akhir_lebih_tinggi", "paruh_awal_lebih_tinggi"}
        return label in moved and keyakinan == ("tinggi" if diff == "easy" else "sedang")
    if task == ANOMALI:
        if diff == "hard":
            return label == "tidak_ada_anomali"
        return label == "ada_anomali" and keyakinan == ("tinggi" if diff == "easy" else "sedang")
    if task == PENJELASAN:
        if diff == "easy":
            return label in {"naik_besar", "turun_besar"}
        if diff == "medium":
            return label in {"naik_kecil", "turun_kecil"}
        return label == "tidak_monoton"
    raise ValueError(task)


def _n_for(task: str, rng: np.random.Generator) -> int:
    return int(rng.integers(24, 41)) if task == ANOMALI else int(rng.integers(18, 41))


def _build_one(task: str, diff: str, sid: str, prof, rng: np.random.Generator):
    """Bangun satu Sample lengkap + baris manifest, atau None bila tak grounded.

    Satu percobaan pembangkitan: deret -> Sample -> build_reference (rantai
    terpendek, hasil dihitung verifier) -> verify_sample. Kembalikan (Sample,row)
    hanya bila 100% grounded DAN (label,keyakinan) cocok maksud kesulitan;
    selain itu None -> pemanggil retry (drop).
    """
    nama, domain, satuan, freq, _ = prof
    n = _n_for(task, rng)
    L = rng.uniform(*prof[4])

    if task == ANOMALI:
        arr, idx, b0, b1 = _gen_anomali(diff, rng, L, n)
        nilai = _round(arr)
        arah = "penurunan" if nilai[idx] < L else "lonjakan"
        ANOMALI_PARAMS[sid] = dict(idx=idx, base=f"nilai[{b0}:{b1}]",
                                   peristiwa=f"{arah} tak biasa")
    else:
        gen = {TREN: _gen_tren, SEGMEN: _gen_segmen, PENJELASAN: _gen_penjelasan}[task]
        nilai = _round(gen(diff, rng, L, n))

    series = Series(nama=nama, satuan=satuan, freq=freq, nilai=nilai)
    konteks = (f"Deret {nama.replace('_', ' ')} ({satuan}), frekuensi {freq}; "
               f"deret sintetis-terkendali untuk pelatihan (domain {domain}).")
    stub = Sample(id=sid, series=series, konteks=konteks, pertanyaan="",
                  reasoning=[], jawaban=None)

    q, reasoning, jawaban, cites = build_reference(stub, task)
    if task == ANOMALI and freq != "tahunan":
        # build_reference menanyakan "tahun dengan ..." (warisan benchmark uji yang
        # semuanya tahunan); untuk deret mingguan/harian pakai "periode".
        q = q.replace("tahun dengan", "periode dengan")
    full = Sample(id=sid, series=series, konteks=konteks, pertanyaan=q,
                  reasoning=reasoning, jawaban=jawaban)

    if verify_sample(full)["grounding_score"] != 100.0:
        return None
    if full.validate():
        return None
    if not _accept(task, diff, jawaban.label, jawaban.keyakinan):
        return None

    row = dict(id=sid, domain=domain, task=task, difficulty=diff,
               n=len(nilai), n_langkah=len(reasoning), cites=cites,
               chain=" ; ".join(s.operasi for s in reasoning),
               label=jawaban.label, keyakinan=jawaban.keyakinan)
    return full, row


def generate() -> tuple[list[Sample], list[dict], int]:
    """Bangkitkan seluruh strata (tugas x kesulitan) secara deterministik.

    -> (samples, rows, total_drop). Deterministik: seed per (task,diff,rep);
    tiap slot menarik dari rng yang sama hingga satu deret diterima (retry).
    """
    samples: list[Sample] = []
    rows: list[dict] = []
    total_drop = 0
    for task in TASKS:
        for diff in DIFFS:
            for rep in range(PER_STRATUM):
                rng = np.random.default_rng(_seed(task, diff, rep))
                prof = PROFILES[rep % len(PROFILES)]
                sid = f"train_{task}_{diff}_{rep:03d}"
                built = None
                for _ in range(MAX_ATTEMPTS):
                    built = _build_one(task, diff, sid, prof, rng)
                    if built is not None:
                        break
                    total_drop += 1
                if built is None:
                    raise RuntimeError(
                        f"gagal membangkitkan {sid} dalam {MAX_ATTEMPTS} percobaan")
                full, row = built
                samples.append(full)
                rows.append(row)
    return samples, rows, total_drop


def check_no_leakage(samples: list[Sample], test_path: Path) -> tuple[int, int]:
    """Assert tak ada deret train identik-numerik dengan deret uji (anti-bocor 9.4).

    -> (n_test_dibandingkan, n_tabrakan). Sumber uji dibaca dari benchmark_acuan
    (ter-commit); bila absen, kembalikan (0,0) — pembangkitan sintetis sudah lepas
    dari WB by construction, cek ini bukti tambahan.
    """
    if not test_path.exists():
        return 0, 0
    test_series = [np.asarray(s.series.nilai, dtype=float) for s in read_jsonl(test_path)]
    collisions = 0
    for s in samples:
        a = np.asarray(s.series.nilai, dtype=float)
        for t in test_series:
            if len(a) == len(t) and np.allclose(a, t, atol=1e-6):
                collisions += 1
                break
    return len(test_series), collisions


def render_manifest(rows: list[dict], n_test: int, drops: int) -> str:
    strata = Counter((r["task"], r["difficulty"]) for r in rows)
    labels = Counter(r["label"] for r in rows)
    lens = Counter(r["n_langkah"] for r in rows)
    domains = Counter(r["domain"] for r in rows)

    lines = [
        "# Manifest — TRAIN Acuan (F4-04)",
        "",
        "Train set fine-tune: rantai operasi acuan **terpendek** atas deret",
        "**sintetis-terkendali** (ADR-0004). Data JSONL:",
        "`data/synthetic/train_acuan.jsonl`; regen dengan",
        "`python scripts/synthesize_train_acuan.py`.",
        "",
        f"**Jumlah:** {len(rows)} sampel. Semua `grounding_score = 100.0` (verifier",
        "di dalam loop; sampel tak-grounded dibuang & dibangkitkan ulang —",
        f"{drops} percobaan dibuang saat pembangkitan). Label bersih by construction.",
        "",
        "**Anti-bocor (9.4):** deret dibangkitkan sendiri, **lepas** dari 18 deret",
        f"WB sumber test; {n_test} deret uji dibandingkan, **0 tabrakan numerik**.",
        "",
        "## Distribusi tugas x kesulitan",
        "",
        "| tugas \\ kesulitan | easy | medium | hard | total |",
        "|---|---|---|---|---|",
    ]
    for task in TASKS:
        e, m, h = (strata[(task, d)] for d in DIFFS)
        lines.append(f"| {task} | {e} | {m} | {h} | {e + m + h} |")
    tot_e, tot_m, tot_h = (sum(strata[(t, d)] for t in TASKS) for d in DIFFS)
    lines.append(f"| **total** | {tot_e} | {tot_m} | {tot_h} | {len(rows)} |")

    lines += ["", "## Distribusi label gold", "",
              "| label | jumlah |", "|---|---|"]
    for lab, c in sorted(labels.items()):
        lines.append(f"| {lab} | {c} |")

    lines += ["", "## Panjang rantai (langkah)", "",
              "| #langkah | jumlah |", "|---|---|"]
    for k, c in sorted(lens.items()):
        lines.append(f"| {k} | {c} |")

    lines += ["", "## Domain", "", "| domain | jumlah |", "|---|---|"]
    for d, c in sorted(domains.items()):
        lines.append(f"| {d} | {c} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    out = _ROOT / "data" / "synthetic" / "train_acuan.jsonl"
    manifest = _ROOT / "data" / "manifest_train_acuan.md"
    test_path = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    samples, rows, drops = generate()

    bad = [s.id for s in samples if verify_sample(s)["grounding_score"] != 100.0]
    if bad:
        print(f"GAGAL: {len(bad)} sampel tidak 100% grounded: {bad[:5]}", file=sys.stderr)
        return 1
    if len(samples) < 300:
        print(f"GAGAL: hanya {len(samples)} sampel (<300).", file=sys.stderr)
        return 1

    n_test, collisions = check_no_leakage(samples, test_path)
    if collisions:
        print(f"GAGAL: {collisions} deret train bocor dari sumber uji.", file=sys.stderr)
        return 1

    write_jsonl(out, samples)
    manifest.write_text(render_manifest(rows, n_test, drops), encoding="utf-8")
    strata = Counter((r["task"], r["difficulty"]) for r in rows)
    print(f"OK: {len(samples)} sampel train (semua 100% grounded) -> {out}")
    print(f"    strata (tugas x kesulitan): {dict(sorted(strata.items()))}")
    print(f"    anti-bocor: {n_test} deret uji dibandingkan, {collisions} tabrakan")
    print(f"    drop saat pembangkitan: {drops}; manifest -> {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
