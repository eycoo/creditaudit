"""Jalur kedua (independen) untuk cross-check verifier — C3 / #5.

Menghitung ulang `expected` tiap operasi TANPA menyentuh `gearts.verifier`
atau `gearts.operations`. Kalau modul ini mengimpor kode itu, cross-check =
menguji-diri-sendiri (sirkular) — itulah yang mau dibantah. Jadi:

  * parser operasi ditulis ulang di sini (regex sendiri),
  * semantik index/slice (batas `b` eksklusif, index negatif) di-resolve tangan
    (bukan lewat slicing NumPy verifier),
  * tiap operasi memakai rumus tangan / NumPy dasar, BUKAN implementasi di
    `operations.py` (mis. `slope` = OLS Σ(x-x̄)(y-ȳ)/Σ(x-x̄)², bukan `np.polyfit`;
    std populasi dihitung manual, bukan lewat fungsi `z_score`).

Satu-satunya dependensi: NumPy. Tak ada impor `gearts`.
"""
from __future__ import annotations

import math
import re

import numpy as np

# --- parser DSL operasi (regex sendiri, tak dipakai bareng verifier) ---------
_OP = re.compile(r"^\s*([a-zA-Z_]\w*)\s*\((.*)\)\s*$")
_SLICE = re.compile(r"^nilai\[(-?\d+):(-?\d+)\]$")
_INDEX = re.compile(r"^nilai\[(-?\d+)\]$")
_LANGKAH = re.compile(r"^langkah\d+$")


class RecomputeError(Exception):
    """Operasi tak bisa dihitung ulang (analog: verifier `expected = None`)."""


def parse(operasi: str) -> tuple[str, list[str]]:
    """'persen_naik(nilai[11]->nilai[15])' -> ('persen_naik', ['nilai[11]','nilai[15]'])."""
    m = _OP.match(operasi)
    if not m:
        raise RecomputeError(f"operasi malformed: {operasi!r}")
    name, inner = m.group(1), m.group(2).strip()
    if not inner:
        return name, []
    parts = inner.split("->") if "->" in inner else inner.split(",")
    return name, [p.strip() for p in parts]


def _norm_index(i: int, n: int) -> int:
    """Resolusi index tangan: negatif -> n+i. Batas dicek eksplisit."""
    j = i if i >= 0 else n + i
    if not (0 <= j < n):
        raise RecomputeError(f"index di luar rentang: {i} (n={n})")
    return j


def _norm_slice(a: int, b: int, n: int) -> tuple[int, int]:
    """Resolusi slice tangan `nilai[a:b]`: b EKSKLUSIF, batas negatif -> n+.

    Ditulis ulang (bukan mengandalkan slicing Python == slicing verifier) supaya
    kesamaan hasil = bukti semantik, bukan kebetulan dua-duanya pakai `series[a:b]`.
    """
    aa = a if a >= 0 else n + a
    bb = b if b >= 0 else n + b
    aa = max(0, min(aa, n))
    bb = max(0, min(bb, n))
    return aa, bb


def _resolve(tok: str, series: list[float], bindings: dict):
    """Token argumen -> nilai (skalar / list) lewat jalur independen."""
    tok = tok.strip()
    n = len(series)
    m = _SLICE.match(tok)
    if m:
        a, b = _norm_slice(int(m.group(1)), int(m.group(2)), n)
        return [float(v) for v in series[a:b]]
    m = _INDEX.match(tok)
    if m:
        return float(series[_norm_index(int(m.group(1)), n)])
    if tok == "nilai":
        return [float(v) for v in series]
    if "=" in tok:  # keyword arg, mis. deteksi_anomali(z=3)
        return float(tok.split("=", 1)[1])
    try:
        return float(tok)
    except ValueError:
        pass
    if tok in bindings:
        return bindings[tok]
    if _LANGKAH.match(tok):
        raise RecomputeError(
            f"referensi langkah tak terikat {tok!r} (forward / non-skalar)")
    raise RecomputeError(f"token tak bisa di-resolve: {tok!r}")


# --- operasi: rumus tangan, NumPy dasar saja (bukan operations.py) -----------
def _mean(xs: list[float]) -> float:
    if not xs:
        raise RecomputeError("mean atas segmen kosong")
    return math.fsum(xs) / len(xs)


def _pop_std(xs: list[float]) -> float:
    """Std populasi (ddof=0) dihitung tangan — harus setara z_score/deteksi_anomali."""
    mu = _mean(xs)
    var = math.fsum((x - mu) ** 2 for x in xs) / len(xs)
    return math.sqrt(var)


def _rata2(seg):
    return _mean(list(seg))


def _delta(a, b):
    return float(b) - float(a)


def _persen_naik(a, b):
    if a == 0:
        raise RecomputeError("persen_naik tak terdefinisi saat basis a==0")
    return (float(b) - float(a)) / float(a) * 100.0


def _rasio(a, b):
    if b == 0:
        raise RecomputeError("rasio tak terdefinisi saat penyebut b==0")
    return float(a) / float(b)


def _slope(seg):
    """OLS slope via Σ(x-x̄)(y-ȳ)/Σ(x-x̄)² — jalur beda dari np.polyfit verifier."""
    y = list(seg)
    n = len(y)
    if n < 2:
        raise RecomputeError("slope butuh >=2 titik")
    x = list(range(n))
    xbar, ybar = _mean(x), _mean(y)
    num = math.fsum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))
    den = math.fsum((xi - xbar) ** 2 for xi in x)
    if den == 0:
        raise RecomputeError("slope tak terdefinisi (varians x nol)")
    return num / den


def _min(seg):
    xs = list(seg)
    if not xs:
        raise RecomputeError("min atas segmen kosong")
    return float(min(xs))


def _max(seg):
    xs = list(seg)
    if not xs:
        raise RecomputeError("max atas segmen kosong")
    return float(max(xs))


def _z_score(x, pop):
    xs = list(pop)
    sd = _pop_std(xs)
    if sd == 0:
        raise RecomputeError("z_score tak terdefinisi saat std populasi 0")
    return (float(x) - _mean(xs)) / sd


def _deteksi_anomali(ambang, pop):
    """Index dua-sisi |z| > ambang atas populasi. Set-valued (list index terurut)."""
    xs = list(pop)
    sd = _pop_std(xs)
    if sd == 0:
        return []
    mu = _mean(xs)
    return [i for i, v in enumerate(xs) if abs((v - mu) / sd) > float(ambang)]


def _bandingkan_segmen(r1, r2):
    return _mean(list(r2)) - _mean(list(r1))


# ops yang butuh populasi penuh (series) di-append saat arg tunggal
_NEEDS_POP = {"z_score", "deteksi_anomali"}
_OPS = {
    "rata2": _rata2, "delta": _delta, "persen_naik": _persen_naik,
    "rasio": _rasio, "slope": _slope, "min": _min, "max": _max,
    "z_score": _z_score, "deteksi_anomali": _deteksi_anomali,
    "bandingkan_segmen": _bandingkan_segmen,
}
_SET_VALUED = {"deteksi_anomali"}


def recompute(operasi: str, series, bindings: dict):
    """Hitung ulang `expected` operasi via jalur independen.

    Return: float (skalar), set[int] (set-valued), atau raise RecomputeError.
    `series` = list angka; `bindings` = {'langkahN': float} dari langkah skalar
    sebelumnya (backward-only, sama kontrak dengan verifier).
    """
    series = [float(v) for v in np.asarray(series, dtype=float).tolist()]
    name, tokens = parse(operasi)
    if name not in _OPS:
        raise RecomputeError(f"operasi tak dikenal: {name}")
    values = [_resolve(t, series, bindings) for t in tokens]
    if name in _NEEDS_POP and len(values) == 1:
        values.append(series)  # populasi implisit = seluruh series
    result = _OPS[name](*values)
    if name in _SET_VALUED:
        return {int(i) for i in result}
    return float(result)


def recompute_sample(sample_dict: dict, abs_tol: float = 0.01,
                     rel_tol: float = 0.01, jaccard_tau: float = 1.0) -> list[dict]:
    """Jalur independen sepenuh-sampel: kembalikan per-langkah expected + grounded.

    Meniru KONTRAK `verify_sample` (skor, binding langkah skalar, toleransi,
    Jaccard set) tapi lewat kode di modul ini — jadi bisa dibandingkan langkah
    demi langkah. Tak mengimpor gearts.
    """
    series = sample_dict["series"]["nilai"]
    bindings: dict = {}
    out: list[dict] = []
    for step in sample_dict["reasoning"]:
        langkah, operasi, claimed = step["langkah"], step["operasi"], step["hasil"]
        try:
            expected = recompute(operasi, series, bindings)
        except RecomputeError as e:
            out.append({"langkah": langkah, "operasi": operasi, "expected": None,
                        "claimed": claimed, "grounded": False, "error": str(e)})
            continue
        if isinstance(expected, set):
            claimed_set = _coerce_set(claimed)
            j = _jaccard(expected, claimed_set)
            out.append({"langkah": langkah, "operasi": operasi,
                        "expected": sorted(expected), "claimed": claimed,
                        "grounded": j >= jaccard_tau, "jaccard": j})
        else:
            bindings[f"langkah{langkah}"] = expected
            ok = abs(expected - float(claimed)) <= max(abs_tol, rel_tol * abs(expected))
            out.append({"langkah": langkah, "operasi": operasi, "expected": expected,
                        "claimed": claimed, "grounded": bool(ok)})
    return out


def _coerce_set(x) -> set[int]:
    if isinstance(x, (list, tuple, set)):
        return {int(i) for i in x}
    return {int(x)}


def _jaccard(a: set[int], b: set[int]) -> float:
    union = a | b
    return 1.0 if not union else len(a & b) / len(union)
