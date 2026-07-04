"""Extraction schema — mirrors project_brief.md Lampiran A exactly.

Field names are Indonesian and canonical: the dataset, M1's constrained
decoding, and every downstream module key on them. Never rename.

# ponytail: stdlib dataclasses + manual validate(); switch to pydantic when
# the dataset pipeline needs bulk validation performance or JSON Schema export.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any

JENIS_PRODUK = {"pinjol", "paylater", "cicilan", "lainnya"}
STATUS_LEGALITAS = {"legal", "ilegal", "tidak diketahui"}
BUNGA_BASIS = {"harian", "bulanan", "tahunan", "flat"}
BIAYA_ADMIN_BASIS = {"persen", "nominal"}
DENDA_BASIS = {"sisa_pokok", "limit_awal", "harian"}


@dataclass
class Produk:
    jenis: str | None = None
    nama_penyelenggara: str | None = None
    status_legalitas_klaim: str | None = None


@dataclass
class TermFinansial:
    pokok: float | None = None
    bunga_nominal: float | None = None
    bunga_basis: str | None = None
    tenor_hari: int | None = None
    biaya_admin: float | None = None
    biaya_admin_basis: str | None = None
    potongan_di_depan: float | None = None
    denda: float | None = None
    denda_basis: str | None = None
    syarat_tersembunyi: list[str] = field(default_factory=list)


@dataclass
class PenandaVisual:
    teks_di_highlight: list[str] = field(default_factory=list)
    teks_fine_print: list[str] = field(default_factory=list)


@dataclass
class Penawaran:
    produk: Produk = field(default_factory=Produk)
    term_finansial: TermFinansial = field(default_factory=TermFinansial)
    penanda_visual: PenandaVisual = field(default_factory=PenandaVisual)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Penawaran":
        """Build from a Lampiran-A-shaped dict. Unknown keys are errors:
        this is the trust boundary for dataset construction, and silent
        key drift would corrupt ground truth."""
        known_sections = {"produk", "term_finansial", "penanda_visual"}
        unknown = set(d) - known_sections
        if unknown:
            raise ValueError(f"unknown top-level keys: {sorted(unknown)}")
        return cls(
            produk=_build(Produk, d.get("produk", {})),
            term_finansial=_build(TermFinansial, d.get("term_finansial", {})),
            penanda_visual=_build(PenandaVisual, d.get("penanda_visual", {})),
        )

    def validate(self) -> list[str]:
        """Return a list of problems; empty list means valid."""
        p, t = self.produk, self.term_finansial
        problems = []
        problems += _check_enum("produk.jenis", p.jenis, JENIS_PRODUK)
        problems += _check_enum(
            "produk.status_legalitas_klaim", p.status_legalitas_klaim, STATUS_LEGALITAS
        )
        problems += _check_enum("term_finansial.bunga_basis", t.bunga_basis, BUNGA_BASIS)
        problems += _check_enum(
            "term_finansial.biaya_admin_basis", t.biaya_admin_basis, BIAYA_ADMIN_BASIS
        )
        problems += _check_enum("term_finansial.denda_basis", t.denda_basis, DENDA_BASIS)
        for name in ("pokok", "bunga_nominal", "tenor_hari", "biaya_admin",
                     "potongan_di_depan", "denda"):
            v = getattr(t, name)
            if v is not None and v < 0:
                problems.append(f"term_finansial.{name} negative: {v}")
        return problems


def _build(cls: type, section: dict[str, Any]):
    known = {f.name for f in fields(cls)}
    unknown = set(section) - known
    if unknown:
        raise ValueError(f"unknown keys in {cls.__name__}: {sorted(unknown)}")
    return cls(**section)


def _check_enum(path: str, value: str | None, allowed: set[str]) -> list[str]:
    if value is not None and value not in allowed:
        return [f"{path} invalid: {value!r} (allowed: {sorted(allowed)})"]
    return []
