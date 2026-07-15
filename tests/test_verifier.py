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


# --- F1-05: non-scalar grounding for deteksi_anomali (ADR-0003 Item 1) ---
# Series [1,1,1,1,10]: mean 2.8, std 3.6, so z of the 10 is +2.0 and z of each 1
# is -0.5. deteksi_anomali(z=1.5) therefore flags exactly index 4 (hand-checked).
DETEKSI = {
    "id": "anomali_001",
    "series": {"nama": "x", "satuan": "unit", "freq": "harian", "nilai": [1, 1, 1, 1, 10]},
    "konteks": "",
    "pertanyaan": "Titik mana yang anomali?",
    "reasoning": [
        {"langkah": 1, "operasi": "deteksi_anomali(z=1.5)", "hasil": [4], "teks": "titik ke-4 anomali"},
    ],
    "jawaban": {"label": "ada_anomali", "keyakinan": "tinggi"},
}


def test_deteksi_anomali_correct_set_grounds():
    r = verify_sample(Sample.from_dict(DETEKSI))
    step = r["steps"][0]
    assert step["grounded"] is True          # boolean, not None
    assert r["grounding_score"] == 100.0      # set step is scored


def test_deteksi_anomali_wrong_set_flagged():
    bad = copy.deepcopy(DETEKSI)
    bad["reasoning"][0]["hasil"] = [3]        # wrong index
    r = verify_sample(Sample.from_dict(bad))
    assert r["steps"][0]["grounded"] is False
    assert r["grounding_score"] == 0.0


def test_deteksi_anomali_jaccard_threshold():
    # claimed {4,5} vs recomputed {4}: Jaccard = 1/2 = 0.5
    partial = copy.deepcopy(DETEKSI)
    partial["reasoning"][0]["hasil"] = [4, 5]
    strict = verify_sample(Sample.from_dict(partial))               # default tau = 1.0 (exact)
    assert strict["steps"][0]["grounded"] is False
    lenient = verify_sample(Sample.from_dict(partial), jaccard_tau=0.5)
    assert lenient["steps"][0]["grounded"] is True


def test_deteksi_anomali_empty_set_grounds():
    # flat series -> std 0 -> no anomalies; claiming none must ground (Jaccard(empty,empty)=1)
    flat = copy.deepcopy(DETEKSI)
    flat["series"]["nilai"] = [5, 5, 5, 5]
    flat["reasoning"][0]["hasil"] = []
    r = verify_sample(Sample.from_dict(flat))
    assert r["steps"][0]["grounded"] is True


def test_set_and_scalar_steps_both_counted():
    mixed = copy.deepcopy(DETEKSI)
    mixed["reasoning"] = [
        {"langkah": 1, "operasi": "rata2(nilai[0:4])", "hasil": 1.0, "teks": "baseline"},
        {"langkah": 2, "operasi": "deteksi_anomali(z=1.5)", "hasil": [4], "teks": "anomali"},
    ]
    r = verify_sample(Sample.from_dict(mixed))
    assert len(r["steps"]) == 2
    assert r["grounding_score"] == 100.0
    # break only the set step -> one of two steps grounded -> 50%
    mixed["reasoning"][1]["hasil"] = [0]
    r2 = verify_sample(Sample.from_dict(mixed))
    assert r2["grounding_score"] == 50.0


# --- F1-06: composite langkah{N} bindings (ADR-0003 Item 4) ---
COMPOSITE = {
    "id": "komposit_001",
    "series": {"nama": "x", "satuan": "unit", "freq": "harian", "nilai": [1, 1, 1, 1, 10]},
    "konteks": "",
    "pertanyaan": "Rasio nilai akhir ke baseline?",
    "reasoning": [
        {"langkah": 1, "operasi": "rata2(nilai[0:4])", "hasil": 1.0, "teks": "baseline"},
        {"langkah": 2, "operasi": "rasio(nilai[4], langkah1)", "hasil": 10.0, "teks": "10x baseline"},
    ],
    "jawaban": {"label": "naik", "keyakinan": "tinggi"},
}


def test_composite_langkah_reference_resolves():
    r = verify_sample(Sample.from_dict(COMPOSITE))
    assert r["grounding_score"] == 100.0
    assert r["steps"][1]["expected"] == 10.0   # rasio(10.0, langkah1=1.0)


def test_langkah_reference_to_nonscalar_step_rejected():
    # step 1 is now a non-scalar (set) result -> not bindable; step 2's langkah1 ref must fail
    bad = copy.deepcopy(COMPOSITE)
    bad["reasoning"][0]["operasi"] = "deteksi_anomali(z=1.5)"
    bad["reasoning"][0]["hasil"] = [4]
    r = verify_sample(Sample.from_dict(bad))
    assert r["steps"][1]["grounded"] is False
    assert "langkah1" in r["steps"][1]["error"]


def test_forward_langkah_reference_rejected():
    # step 1 references step 2, which has not been computed yet -> must fail
    bad = copy.deepcopy(COMPOSITE)
    bad["reasoning"][0]["operasi"] = "rasio(nilai[4], langkah2)"
    r = verify_sample(Sample.from_dict(bad))
    assert r["steps"][0]["grounded"] is False
    assert "langkah2" in r["steps"][0]["error"]
