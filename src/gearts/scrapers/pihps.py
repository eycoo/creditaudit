"""PIHPS / Bank Indonesia daily food-price scraper (F4-02).

Turns the PIHPS Nasional daily price grid into raw `Series` JSONL matching
`gearts.schema.Series`. Default source per `project_brief.md` §9.1;
normalization per §10.1 (unit, frequency, missing values, number format).

Design (per builder.md / ADR-0002):
- `fetch_pihps` is the only network code; it returns a list of plain records
  `{"tanggal": "YYYY-MM-DD", "harga": "<id-number-string>"}`.
- `parse_id_number` and `records_to_series` are pure and fully unit-tested.
- No reasoning is synthesized here — series only.

NOTE (endpoint): PIHPS has no documented official REST API. The dashboard at
https://www.bi.go.id/hargapangan serves a JSON grid from an internal endpoint
whose exact shape must be re-verified before a real run (see
`.scratch/fase-1-fondasi/sumber-deret.md`). `fetch_pihps` therefore isolates
that fragile step; if the endpoint shape differs, only `fetch_pihps` changes,
not the tested normalization.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from gearts.schema import Series, write_series_jsonl

log = logging.getLogger(__name__)

# Internal grid endpoint behind the BI hargapangan dashboard. Re-verify the
# path, params, and response shape before a live scrape (portal changes often).
PIHPS_ENDPOINT = "https://www.bi.go.id/hargapangan/WebSite/Home/GetGridDataDaily"

# Missing-value sentinels seen in the PIHPS grid.
_MISSING = {"", "-", "n/a", "na", "null"}


def parse_id_number(raw: Any) -> float | None:
    """Parse an Indonesian-formatted number string to float, else `None`.

    Indonesian format: `.` is the thousands separator, `,` is the decimal
    separator — e.g. ``"13.100,50"`` → ``13100.50``, ``"12.500"`` → ``12500.0``.
    Returns `None` for missing sentinels (``""``, ``"-"``, `None`, …) and for
    anything non-numeric, so callers can log-and-skip.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if s.lower() in _MISSING:
        return None
    # Comma present → it is the decimal mark; dots are thousands separators.
    # No comma → dots are thousands separators.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def records_to_series(
    records: Iterable[dict[str, Any]],
    *,
    nama: str,
    satuan: str,
    freq: str = "harian",
) -> Series:
    """Normalize raw `{tanggal, harga}` records into a clean `Series`.

    - Parses each `harga` via `parse_id_number`; logs and **skips** rows whose
      value is missing or malformed (keeps `nilai` a clean numeric array).
    - Sorts remaining points chronologically (ISO dates sort lexicographically).
    - Sets standardized `satuan` and `freq`.

    Raises `ValueError` if no valid points remain after cleaning.
    """
    points: list[tuple[str, float]] = []
    for row in records:
        tanggal = str(row.get("tanggal", "")).strip()
        value = parse_id_number(row.get("harga"))
        if value is None:
            log.warning("skip malformed/missing row: %r", row)
            continue
        points.append((tanggal, value))

    if not points:
        raise ValueError(f"no valid values after cleaning for series {nama!r}")

    points.sort(key=lambda p: p[0])
    return Series(nama=nama, satuan=satuan, freq=freq, nilai=[v for _, v in points])


def fetch_pihps(
    *,
    komoditas_id: int,
    start: str,
    end: str,
    endpoint: str = PIHPS_ENDPOINT,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """Fetch daily price rows from the PIHPS grid endpoint (NETWORK).

    Returns a list of `{"tanggal": "YYYY-MM-DD", "harga": "<id-number>"}`.
    Not unit-tested (hits the network); the fragile response mapping is kept
    thin so a shape change is contained here. Re-verify `PIHPS_ENDPOINT` and the
    param/response shape before use (see module docstring).
    """
    params = urllib.parse.urlencode(
        {"commodityId": komoditas_id, "startDate": start, "endDate": end}
    )
    url = f"{endpoint}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "gearts-scraper/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (public gov data)
        payload = json.loads(resp.read().decode("utf-8"))
    return _extract_rows(payload)


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    """Map the BI grid payload to `{tanggal, harga}` records.

    Tolerant to the two shapes the dashboard has served: a top-level list, or a
    `{"data": [...]}` envelope. Each item is expected to expose a date and a
    price field under any of a few known key spellings.
    """
    items = payload["data"] if isinstance(payload, dict) and "data" in payload else payload
    rows: list[dict[str, Any]] = []
    for it in items:
        tanggal = it.get("tanggal") or it.get("date") or it.get("Tanggal")
        harga = it.get("harga") or it.get("price") or it.get("Harga")
        rows.append({"tanggal": tanggal, "harga": harga})
    return rows


def scrape_to_jsonl(
    *,
    komoditas_id: int,
    nama: str,
    start: str,
    end: str,
    satuan: str = "rupiah/kg",
    out_path: str | Path = "data/raw/pihps.jsonl",
) -> Series:
    """End-to-end: fetch PIHPS → normalize → write one `Series` to JSONL."""
    records = fetch_pihps(komoditas_id=komoditas_id, start=start, end=end)
    series = records_to_series(records, nama=nama, satuan=satuan)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    write_series_jsonl(out_path, [series])
    log.info("wrote %d points to %s", len(series.nilai), out_path)
    return series


if __name__ == "__main__":  # pragma: no cover
    import argparse

    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Scrape one PIHPS commodity -> JSONL")
    ap.add_argument("--komoditas-id", type=int, required=True)
    ap.add_argument("--nama", required=True, help="series name, e.g. beras_medium")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", default="data/raw/pihps.jsonl")
    args = ap.parse_args()
    scrape_to_jsonl(
        komoditas_id=args.komoditas_id,
        nama=args.nama,
        start=args.start,
        end=args.end,
        out_path=args.out,
    )
