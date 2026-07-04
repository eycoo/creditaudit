import pytest

from creditaudit.schema import Penawaran

LAMPIRAN_B = {
    "produk": {
        "jenis": "pinjol",
        "nama_penyelenggara": None,
        "status_legalitas_klaim": "tidak diketahui",
    },
    "term_finansial": {
        "pokok": 1_000_000,
        "bunga_nominal": 0.4,
        "bunga_basis": "harian",
        "tenor_hari": 30,
        "biaya_admin": 10,
        "biaya_admin_basis": "persen",
        "potongan_di_depan": 100_000,
        "syarat_tersembunyi": ["potongan admin 10% di depan"],
    },
    "penanda_visual": {
        "teks_di_highlight": ["bunga cuma 0,4% per hari"],
        "teks_fine_print": ["potongan admin 10% di depan, tenor 30 hari"],
    },
}


def test_lampiran_b_roundtrip_valid():
    p = Penawaran.from_dict(LAMPIRAN_B)
    assert p.validate() == []
    assert p.term_finansial.pokok == 1_000_000
    assert p.penanda_visual.teks_di_highlight == ["bunga cuma 0,4% per hari"]


def test_invalid_enum_reported():
    p = Penawaran.from_dict(LAMPIRAN_B)
    p.term_finansial.denda_basis = "limit_akhir"  # not in DENDA_BASIS
    problems = p.validate()
    assert len(problems) == 1 and "denda_basis" in problems[0]


def test_negative_number_reported():
    p = Penawaran.from_dict(LAMPIRAN_B)
    p.term_finansial.pokok = -5
    assert any("pokok" in x for x in p.validate())


def test_unknown_key_rejected():
    bad = {**LAMPIRAN_B, "term_finansial": {**LAMPIRAN_B["term_finansial"], "bunga": 1}}
    with pytest.raises(ValueError, match="bunga"):
        Penawaran.from_dict(bad)
