"""Calculator tests keyed to project_brief.md Lampiran B — the worked example
is the contract: if these numbers drift, ground-truth labels drift with them."""
import pytest

from creditaudit.calculator import hitung_biaya
from creditaudit.schema import TermFinansial


def lampiran_b_term(**overrides) -> TermFinansial:
    base = dict(
        pokok=1_000_000,
        bunga_nominal=0.4,
        bunga_basis="harian",
        tenor_hari=30,
        biaya_admin=10,
        biaya_admin_basis="persen",
        potongan_di_depan=100_000,
    )
    base.update(overrides)
    return TermFinansial(**base)


def test_lampiran_b():
    b = hitung_biaya(lampiran_b_term())
    assert b.dana_bersih_diterima == 900_000
    assert b.total_bunga == 120_000
    assert b.total_bayar == 1_120_000
    assert round(b.biaya_efektif_persen_bulan, 1) == 24.4


def test_potongan_derived_from_admin_persen():
    b = hitung_biaya(lampiran_b_term(potongan_di_depan=None))
    assert b.dana_bersih_diterima == 900_000  # 10% of pokok


def test_admin_nominal():
    b = hitung_biaya(lampiran_b_term(potongan_di_depan=None,
                                     biaya_admin=50_000, biaya_admin_basis="nominal"))
    assert b.dana_bersih_diterima == 950_000


def test_bunga_bulanan_converts_to_daily():
    harian = hitung_biaya(lampiran_b_term())
    bulanan = hitung_biaya(lampiran_b_term(bunga_nominal=12, bunga_basis="bulanan"))
    assert bulanan.total_bunga == harian.total_bunga  # 12%/bulan == 0.4%/hari


def test_missing_required_fields_raise():
    with pytest.raises(ValueError):
        hitung_biaya(lampiran_b_term(pokok=None))
    with pytest.raises(ValueError):
        hitung_biaya(lampiran_b_term(tenor_hari=0))


def test_flat_basis_fails_loud():
    with pytest.raises(ValueError, match="bunga_basis"):
        hitung_biaya(lampiran_b_term(bunga_basis="flat"))


def test_upfront_cut_consuming_pokok_raises():
    with pytest.raises(ValueError):
        hitung_biaya(lampiran_b_term(potongan_di_depan=1_000_000))
