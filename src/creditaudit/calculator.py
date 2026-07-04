"""Deterministic cost calculator — the executor for M2's program-of-thought.

ADR-0002: ALL arithmetic for audited figures lives here — ground-truth
labels, inference, and evaluation all call these functions. Pure, no I/O.

Verified against the brief's worked example (Lampiran B):
pokok 1_000_000, bunga 0.4%/hari, tenor 30, admin 10% di depan
-> dana bersih 900_000, bunga 120_000, total bayar 1_120_000, ~24.4%/bulan.
"""
from __future__ import annotations

from dataclasses import dataclass

from creditaudit.schema import TermFinansial

HARI_PER_BULAN = 30  # monthly-cost convention used by the brief's examples


@dataclass
class BiayaSebenarnya:
    """True cost — shaped like the brief's `biaya_sebenarnya` output block."""
    dana_bersih_diterima: float
    total_bunga: float
    total_bayar: float
    biaya_efektif_persen_bulan: float


def hitung_biaya(term: TermFinansial) -> BiayaSebenarnya:
    if term.pokok is None or term.bunga_nominal is None or term.tenor_hari is None:
        raise ValueError("pokok, bunga_nominal, and tenor_hari are required")
    if term.tenor_hari <= 0:
        raise ValueError(f"tenor_hari must be positive: {term.tenor_hari}")

    potongan = _potongan_di_depan(term)
    dana_bersih = term.pokok - potongan
    if dana_bersih <= 0:
        raise ValueError(f"upfront cuts ({potongan}) consume the whole pokok ({term.pokok})")

    total_bunga = term.pokok * _bunga_harian_persen(term) / 100 * term.tenor_hari
    total_bayar = term.pokok + total_bunga

    # effective monthly cost relative to funds actually received (Lampiran B)
    biaya_total = total_bayar - dana_bersih
    persen_bulan = biaya_total / dana_bersih * (HARI_PER_BULAN / term.tenor_hari) * 100

    return BiayaSebenarnya(
        dana_bersih_diterima=dana_bersih,
        total_bunga=total_bunga,
        total_bayar=total_bayar,
        biaya_efektif_persen_bulan=persen_bulan,
    )


def _potongan_di_depan(term: TermFinansial) -> float:
    """Explicit potongan_di_depan wins (it's the resolved figure, per Lampiran B
    where both it and biaya_admin describe the same 10% cut); otherwise derive
    from biaya_admin."""
    if term.potongan_di_depan is not None:
        return term.potongan_di_depan
    if term.biaya_admin is None:
        return 0.0
    if term.biaya_admin_basis == "persen":
        return term.pokok * term.biaya_admin / 100
    return term.biaya_admin  # "nominal" or unspecified: treat as rupiah


def _bunga_harian_persen(term: TermFinansial) -> float:
    """Daily simple-interest rate in percent.

    # ponytail: harian/bulanan/tahunan only; 'flat' needs a per-tenor semantics
    # decision (researcher issue) before it can be converted — fail loud until then.
    """
    if term.bunga_basis == "harian":
        return term.bunga_nominal
    if term.bunga_basis == "bulanan":
        return term.bunga_nominal / HARI_PER_BULAN
    if term.bunga_basis == "tahunan":
        return term.bunga_nominal / 360
    raise ValueError(f"unsupported bunga_basis: {term.bunga_basis!r}")
