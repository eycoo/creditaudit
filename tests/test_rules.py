from creditaudit.calculator import hitung_biaya
from creditaudit.rules import cek_kepatuhan
from creditaudit.schema import TermFinansial


def make(bunga_nominal, tenor_hari=30):
    term = TermFinansial(pokok=1_000_000, bunga_nominal=bunga_nominal,
                         bunga_basis="harian", tenor_hari=tenor_hari)
    return term, hitung_biaya(term)


def test_lampiran_b_case_flags_bunga():
    hasil = cek_kepatuhan(*make(0.4))
    assert hasil["melebihi_batas_bunga"] is True
    assert "0,4" in hasil["catatan"] and "0,1" in hasil["catatan"]


def test_compliant_rate_passes():
    hasil = cek_kepatuhan(*make(0.08))
    assert hasil["melebihi_batas_bunga"] is False
    assert hasil["melebihi_lock_cap"] is False


def test_lock_cap():
    # 0.4%/day over 300 days -> total bunga 120% of pokok
    hasil = cek_kepatuhan(*make(0.4, tenor_hari=300))
    assert hasil["melebihi_lock_cap"] is True


def test_boundary_rate_is_compliant():
    hasil = cek_kepatuhan(*make(0.1))  # cap is "maksimal 0,1%" -> equal is legal
    assert hasil["melebihi_batas_bunga"] is False
