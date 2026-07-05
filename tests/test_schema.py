"""Schema tests — Lampiran A roundtrip + validation."""
import copy

import pytest

from gearts.schema import Sample, read_jsonl, write_jsonl

LAMPIRAN_B = {
    "id": "dbd_kabX_001",
    "series": {"nama": "kasus_dbd_mingguan", "satuan": "kasus", "freq": "mingguan",
               "nilai": [12, 15, 11, 14, 13, 18, 22, 19, 25, 31, 29, 38, 45, 52, 61, 78]},
    "konteks": "Kasus DBD mingguan Kabupaten X, 16 minggu",
    "pertanyaan": "Apakah ada indikasi outbreak?",
    "reasoning": [
        {"langkah": 1, "operasi": "rata2(nilai[0:5])", "hasil": 13.0, "teks": "baseline"},
        {"langkah": 2, "operasi": "persen_naik(nilai[11]->nilai[15])", "hasil": 105.3, "teks": "naik"},
        {"langkah": 3, "operasi": "rasio(nilai[15], 13.0)", "hasil": 6.0, "teks": "6x"},
    ],
    "jawaban": {"label": "outbreak", "keyakinan": "tinggi"},
}


def test_valid_sample():
    assert Sample.from_dict(LAMPIRAN_B).validate() == []


def test_jsonl_roundtrip(tmp_path):
    s = Sample.from_dict(LAMPIRAN_B)
    p = tmp_path / "d.jsonl"
    write_jsonl(p, [s])
    got = read_jsonl(p)
    assert len(got) == 1
    assert got[0].to_dict() == s.to_dict()


def test_bad_freq_reported():
    d = copy.deepcopy(LAMPIRAN_B)
    d["series"]["freq"] = "per-fortnight"
    assert any("freq" in x for x in Sample.from_dict(d).validate())


def test_unknown_operation_reported():
    d = copy.deepcopy(LAMPIRAN_B)
    d["reasoning"][0]["operasi"] = "bogus(nilai[0:5])"
    assert any("operasi" in x for x in Sample.from_dict(d).validate())


def test_empty_series_reported():
    d = copy.deepcopy(LAMPIRAN_B)
    d["series"]["nilai"] = []
    assert any("nilai" in x for x in Sample.from_dict(d).validate())


def test_unknown_key_rejected():
    d = copy.deepcopy(LAMPIRAN_B)
    d["series"]["extra"] = 1
    with pytest.raises(ValueError, match="extra"):
        Sample.from_dict(d)
