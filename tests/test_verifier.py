"""Verifier tests — the grounding metric the project stands on.

Lampiran B (honest reasoning) must score 100%. A Lampiran D hallucination
(claiming +30% where the series rose +105%) must be caught: that step
ungrounded, score drops to 66.7%.
"""
import copy

import pytest

from gearts.schema import Sample
from gearts.verifier import eval_step, parse_operasi, verify_sample

LAMPIRAN_B = {
    "id": "dbd_kabX_001",
    "series": {"nama": "kasus_dbd_mingguan", "satuan": "kasus", "freq": "mingguan",
               "nilai": [12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78]},
    "konteks": "Kasus DBD mingguan Kabupaten X, 16 minggu",
    "pertanyaan": "Apakah ada indikasi outbreak?",
    "reasoning": [
        {"langkah": 1, "operasi": "rata2(nilai[0:5])", "hasil": 13.0, "teks": "baseline awal 13 kasus"},
        {"langkah": 2, "operasi": "persen_naik(nilai[11]->nilai[15])", "hasil": 105.3,
         "teks": "minggu 12 ke 16 naik 105%"},
        {"langkah": 3, "operasi": "rasio(nilai[15], 13.0)", "hasil": 6.0, "teks": "nilai akhir 6x baseline"},
    ],
    "jawaban": {"label": "outbreak", "keyakinan": "tinggi"},
}


def test_lampiran_b_full_grounding():
    r = verify_sample(Sample.from_dict(LAMPIRAN_B))
    assert r["grounding_score"] == 100.0
    assert all(s["grounded"] for s in r["steps"])


def test_hallucinated_magnitude_flagged():
    bad = copy.deepcopy(LAMPIRAN_B)
    bad["reasoning"][1]["hasil"] = 30.0  # "salah besaran" (Lampiran D)
    r = verify_sample(Sample.from_dict(bad))
    assert round(r["grounding_score"], 1) == 66.7
    assert r["steps"][1]["grounded"] is False


def test_rounded_claim_still_grounds():
    # exact persen_naik is 105.26; the presented 105.3 must not be flagged
    r = verify_sample(Sample.from_dict(LAMPIRAN_B))
    assert r["steps"][1]["grounded"] is True


def test_unknown_operation_is_ungrounded():
    bad = copy.deepcopy(LAMPIRAN_B)
    bad["reasoning"][0]["operasi"] = "bogus(nilai[0:5])"
    r = verify_sample(Sample.from_dict(bad))
    assert r["steps"][0]["grounded"] is False


def test_parse_malformed_raises():
    with pytest.raises(ValueError):
        parse_operasi("not an operation")


def test_eval_step_slice_and_index():
    import numpy as np
    series = np.array(LAMPIRAN_B["series"]["nilai"], dtype=float)
    assert eval_step("rata2(nilai[0:5])", series, {}) == 13.0
    assert eval_step("max(nilai)", series, {}) == 78.0
