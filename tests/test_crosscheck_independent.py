"""Jalur independen == verifier di fixture Lampiran B (C3 / #5).

Menegakkan kontrak cross-check: `experiments/verifier-crosscheck/independent.py`
(NumPy murni, tanpa `gearts`) menghasilkan `expected` yang sama dengan
`gearts.verifier.verify_sample` pada fixture Lampiran B/D dan turunannya. Kalau
suatu saat dua jalur berbeda, itu bug — dan test ini merah.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "experiments" / "verifier-crosscheck"))

import independent  # noqa: E402  (jalur kedua)
from gearts.schema import Sample  # noqa: E402
from gearts.verifier import verify_sample  # noqa: E402
from test_verifier import COMPOSITE, DETEKSI, LAMPIRAN_B  # noqa: E402


def _expected_equal(ve, ie) -> bool:
    if ve is None or ie is None:
        return ve is None and ie is None
    if isinstance(ve, list) or isinstance(ie, list):
        return sorted(ve) == sorted(ie)
    return abs(float(ve) - float(ie)) <= 1e-9 + 1e-9 * abs(float(ve))


def _assert_two_paths_agree(sample_dict):
    v = verify_sample(Sample.from_dict(sample_dict))
    i_by_langkah = {s["langkah"]: s for s in independent.recompute_sample(sample_dict)}
    for vstep in v["steps"]:
        istep = i_by_langkah[vstep["langkah"]]
        assert _expected_equal(vstep.get("expected"), istep.get("expected")), (
            f"langkah {vstep['langkah']}: verifier={vstep.get('expected')} "
            f"!= independen={istep.get('expected')}")
        # verdikt grounded juga harus sepakat (skalar & set-valued)
        if vstep.get("grounded") is not None:
            assert bool(vstep["grounded"]) == bool(istep["grounded"])


def test_independent_matches_verifier_lampiran_b():
    _assert_two_paths_agree(LAMPIRAN_B)


def test_independent_matches_verifier_deteksi_set_valued():
    _assert_two_paths_agree(DETEKSI)


def test_independent_matches_verifier_composite_langkah_refs():
    _assert_two_paths_agree(COMPOSITE)


def test_independent_module_does_not_import_gearts():
    # Kontrak inti C3: jalur kedua tak boleh menyentuh gearts (kalau tidak,
    # cross-check = menguji-diri-sendiri). Jaga lewat inspeksi sumber.
    src = (_ROOT / "experiments" / "verifier-crosscheck" / "independent.py").read_text(
        encoding="utf-8")
    assert "import gearts" not in src
    assert "from gearts" not in src
