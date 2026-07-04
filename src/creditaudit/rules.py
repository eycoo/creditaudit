"""OJK compliance rule engine (M3) — deterministic, never trained (ADR-0001).

Thresholds encode *versioned* regulation (SEOJK 19/SEOJK.06/2023 phase-down,
POJK 32/2025); verify against current OJK rules before relying on them.
"""
from __future__ import annotations

from creditaudit.calculator import HARI_PER_BULAN, BiayaSebenarnya
from creditaudit.schema import TermFinansial

BATAS_BUNGA_HARIAN_PERSEN = 0.1  # consumptive-loan cap, 2026 target
BATAS_LOCK_CAP_PERSEN = 100.0    # total beban (bunga + denda) <= 100% of pokok


def cek_kepatuhan(term: TermFinansial, biaya: BiayaSebenarnya) -> dict:
    """Return the brief's `kepatuhan_ojk` output block."""
    catatan: list[str] = []

    melebihi_bunga = False
    bunga_harian = _bunga_harian_persen(term)
    if bunga_harian is None:
        catatan.append(
            f"bunga_basis {term.bunga_basis!r} tidak dapat dikonversi ke harian; "
            "batas bunga tidak diperiksa"
        )
    elif bunga_harian > BATAS_BUNGA_HARIAN_PERSEN:
        melebihi_bunga = True
        catatan.append(
            f"Bunga harian {_id_num(bunga_harian)}% di atas batas konsumtif "
            f"{_id_num(BATAS_BUNGA_HARIAN_PERSEN)}% per hari"
        )

    # ponytail: lock cap checks bunga only until denda math lands
    # (.scratch/fase-1-fondasi/issues/02-calculator-denda-basis.md)
    melebihi_lock_cap = biaya.total_bunga > term.pokok * BATAS_LOCK_CAP_PERSEN / 100
    if melebihi_lock_cap:
        catatan.append(
            f"Total bunga Rp{biaya.total_bunga:,.0f} melebihi "
            f"{_id_num(BATAS_LOCK_CAP_PERSEN)}% pokok (lock cap)"
        )

    return {
        "melebihi_batas_bunga": melebihi_bunga,
        "melebihi_lock_cap": melebihi_lock_cap,
        "catatan": "; ".join(catatan) if catatan else "Tidak ada pelanggaran terdeteksi",
    }


def _bunga_harian_persen(term: TermFinansial) -> float | None:
    if term.bunga_nominal is None:
        return None
    if term.bunga_basis == "harian":
        return term.bunga_nominal
    if term.bunga_basis == "bulanan":
        return term.bunga_nominal / HARI_PER_BULAN
    if term.bunga_basis == "tahunan":
        return term.bunga_nominal / 360
    return None  # 'flat' / unknown: don't guess a daily rate in a compliance check


def _id_num(x: float) -> str:
    """0.4 -> '0,4' (Indonesian decimal comma, no trailing zeros)."""
    return f"{x:g}".replace(".", ",")
