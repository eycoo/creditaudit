"""BPS Web API scraper — real Indonesian statistical time series (F4-03).

Second **real** train source (CONCERNS C5): the deterministic verifier grounds
reasoning regardless of series origin, but a data-mining paper is stronger when
the train *series* are real. World Bank indicators are the held-out TEST source
(`benchmark_uji`); §9.4 anti-leak forbids reusing them for train, so train needs
a DIFFERENT real provider. BPS (Badan Pusat Statistik) is that provider: an
official JSON REST API (`webapi.bps.go.id`), free registered key, clear ToS,
disjoint from World Bank by construction.

Design (mirrors `pihps.py` / ADR-0002):
- Only `fetch_json` / `list_periods` / `fetch_var_data` touch the network.
- `datacontent_key` and `build_series` are **pure** and fully unit-tested — the
  fragile part (network + the composite-key encoding) is isolated so a portal
  change touches one place, not the tested normalization.
- No reasoning is synthesized here — series only.

BPS `datacontent` encoding (decoded empirically 2026-07-17, var 70):
a flat object mapping a **composite string key** to one numeric value, where the
key is the concatenation ``f"{vervar}{var}{turvar}{th}{turtahun}"`` of the ids
from the response's own metadata lists. Example: ``"6100702111220"`` =
vervar ``6100`` + var ``70`` + turvar ``211`` + th ``122`` (2022) + turtahun ``0``.
We CONSTRUCT keys from known ids (never parse), so variable-length ids are
unambiguous.

API quirks handled:
- A WAF (Perimeter/Imperva) blocks empty/curl User-Agents → a browser UA is sent.
- The `data` model caps the `th` (period) parameter at **3 years per request** →
  `fetch_var_data` chunks periods into groups of <=3 and merges `datacontent`.

The API key is a credential; this repo is PUBLIC. The key is read from the
`BPS_API_KEY` env var (or passed explicitly) and is NEVER hardcoded or committed.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from gearts.schema import Series, write_series_jsonl

log = logging.getLogger(__name__)

BPS_BASE = "https://webapi.bps.go.id/v1/api/list"
# The WAF rejects non-browser User-Agents; send a realistic desktop UA.
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
_TH_MAX_PER_REQ = 3  # API hard limit: max 3 years per `th` parameter.
_MISSING = {"", "-", "n/a", "na", "null", "none"}


# --- pure: key construction + normalization (unit-tested, no network) ----------

def datacontent_key(vervar: int, var: int, turvar: int, th: int, turtahun: int) -> str:
    """Compose the BPS `datacontent` lookup key from its component ids.

    The key is the plain string concatenation of the ids exactly as BPS encodes
    it: ``vervar || var || turvar || th || turtahun``. Constructing (not parsing)
    keeps variable-length ids unambiguous.
    """
    return f"{vervar}{var}{turvar}{th}{turtahun}"


def _to_float(raw: Any) -> float | None:
    """BPS values are JSON numbers, but tolerate string/sentinel forms."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    if s.lower() in _MISSING:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def build_series(
    payload: dict[str, Any],
    *,
    vervar: int,
    turvar: int = 0,
    turtahun: int = 0,
    nama: str | None = None,
    freq: str = "tahunan",
) -> Series:
    """Assemble ONE clean `Series` for a (vervar, turvar) slice from a data payload.

    `payload` is a merged BPS `data`-model response (see `fetch_var_data`): it
    must carry `var`, `tahun`, and `datacontent`. Periods are ordered
    chronologically by their year label; points whose key is missing/malformed in
    `datacontent` are logged and skipped. Raises `ValueError` if nothing remains.
    """
    var_id = int(payload["var"][0]["val"])
    unit = str(payload["var"][0].get("unit") or "").strip()
    label = str(payload["var"][0].get("label") or f"var_{var_id}")
    # tahun: [{"val": th_id, "label": "2021"}]; sort by numeric year label.
    tahun = sorted(payload["tahun"], key=lambda t: int(str(t["label"])[:4]))
    dc = payload["datacontent"]

    nilai: list[float] = []
    for t in tahun:
        key = datacontent_key(vervar, var_id, turvar, int(t["val"]), turtahun)
        val = _to_float(dc.get(key))
        if val is None:
            log.warning("missing/malformed datacontent[%s] (%s)", key, t.get("label"))
            continue
        nilai.append(val)

    if not nilai:
        raise ValueError(
            f"no values for vervar={vervar} turvar={turvar} in var {var_id}"
        )
    return Series(nama=nama or _slug(label), satuan=unit or "-", freq=freq, nilai=nilai)


def _slug(label: str) -> str:
    keep = [c.lower() if c.isalnum() else "_" for c in label.strip()]
    s = "".join(keep)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")[:60] or "bps_series"


def _chunk(seq: list[int], size: int) -> Iterable[list[int]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def pick_id(items: list[dict[str, Any]], prefer: str | None) -> int:
    """Pick one metadata id by label preference (regex), else the first.

    Many BPS variables carry a derived dimension — turvar (e.g. Perkotaan /
    Perdesaan / **Jumlah**) or turtahun (Semester 1 / Semester 2 / **Tahunan**).
    For a single clean series we select one level per variable, preferring the
    aggregate/annual label; `prefer=None` (or no match) falls back to the first.
    """
    if not items:
        return 0
    if prefer:
        pat = re.compile(prefer, re.I)
        for it in items:
            if pat.search(str(it.get("label", ""))):
                return int(it["val"])
    return int(items[0]["val"])


def _coverage(payload: dict[str, Any], vervar: int, turvar: int, turtahun: int) -> int:
    """Count non-missing datacontent points for one (vervar,turvar,turtahun) slice."""
    var_id = int(payload["var"][0]["val"])
    dc = payload["datacontent"]
    hits = 0
    for t in payload.get("tahun", []):
        if _to_float(dc.get(datacontent_key(vervar, var_id, turvar, int(t["val"]), turtahun))) is not None:
            hits += 1
    return hits


def best_levels(
    payload: dict[str, Any],
    *,
    turvar_prefer: str | None = None,
    turtahun_prefer: str | None = None,
) -> tuple[int, int]:
    """Choose the (turvar, turtahun) pair that actually carries the most data.

    BPS often exposes derived levels with NO datacontent (e.g. an unpopulated
    "Tahunan" aggregate over semester-only poverty data). Label preference alone
    silently yields empty series, so we pick the combination with maximum point
    coverage on a reference vervar, using the label preference only to break ties.
    """
    turvars = payload.get("turvar", [{"val": 0}]) or [{"val": 0}]
    turtahuns = payload.get("turtahun", [{"val": 0}]) or [{"val": 0}]
    vervars = payload.get("vervar", [{"val": 0}]) or [{"val": 0}]
    ref = int(vervars[0]["val"])
    pref_tv = pick_id(turvars, turvar_prefer)
    pref_tt = pick_id(turtahuns, turtahun_prefer)
    best, best_key = None, (-1, 0, 0)
    for tv in turvars:
        for tt in turtahuns:
            tv_id, tt_id = int(tv["val"]), int(tt["val"])
            cov = _coverage(payload, ref, tv_id, tt_id)
            # rank: coverage first, then match to preferred labels (tie-break)
            rank = (cov, int(tv_id == pref_tv), int(tt_id == pref_tt))
            if rank > best_key:
                best_key, best = rank, (tv_id, tt_id)
    return best if best else (pref_tv, pref_tt)


# --- network: the only fragile, untested-by-network parts ----------------------

def _resolve_key(key: str | None) -> str:
    key = key or os.environ.get("BPS_API_KEY")
    if not key:
        raise RuntimeError(
            "BPS API key missing: pass key=... or set BPS_API_KEY env var "
            "(never hardcode it — this repo is public)."
        )
    return key


def fetch_json(path: str, *, key: str | None = None, timeout: float = 30.0) -> dict[str, Any]:
    """GET one BPS API path (below `/model/...`) and return parsed JSON.

    Sends a browser UA (WAF) and appends `/key/<KEY>`. Raises on WAF blocks and
    on `status != OK` so callers fail loudly instead of silently emptily.
    """
    k = _resolve_key(key)
    url = f"{BPS_BASE}/{path.strip('/')}/key/{k}"
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (public gov API)
        body = resp.read().decode("utf-8")
    if body.lstrip().startswith("<"):
        raise RuntimeError(f"BPS returned non-JSON (WAF block?) for /{path}")
    data = json.loads(body)
    if str(data.get("status")).upper() != "OK":
        raise RuntimeError(f"BPS error for /{path}: {data.get('message', data.get('status'))}")
    return data


def list_periods(domain: str, var: int, *, key: str | None = None) -> list[dict[str, Any]]:
    """List available periods for a variable → ``[{"th_id": int, "th": "2023"}, ...]``."""
    data = fetch_json(f"model/th/domain/{domain}/var/{var}", key=key)
    rows = data["data"][1] if isinstance(data.get("data"), list) and len(data["data"]) > 1 else []
    return [{"th_id": int(r["th_id"]), "th": str(r["th"])} for r in rows]


def fetch_var_data(
    domain: str,
    var: int,
    th_ids: list[int],
    *,
    key: str | None = None,
    pause: float = 0.3,
) -> dict[str, Any]:
    """Fetch a variable's data over `th_ids`, chunking to the 3-year API cap.

    Returns a single merged payload (`var`, `vervar`, `turvar`, `tahun`,
    `turtahun`, `datacontent`) suitable for `build_series`. Metadata lists are
    taken from the first non-empty chunk; `tahun` and `datacontent` accumulate.
    """
    merged: dict[str, Any] = {"datacontent": {}, "tahun": []}
    seen_th: set[int] = set()
    for chunk in _chunk(sorted(set(th_ids)), _TH_MAX_PER_REQ):
        th_param = ";".join(str(t) for t in chunk)
        data = fetch_json(f"model/data/domain/{domain}/var/{var}/th/{th_param}", key=key)
        for meta in ("var", "vervar", "turvar", "turtahun"):
            if meta not in merged and isinstance(data.get(meta), list):
                merged[meta] = data[meta]
        for t in data.get("tahun", []):
            if int(t["val"]) not in seen_th:
                merged["tahun"].append(t)
                seen_th.add(int(t["val"]))
        merged["datacontent"].update(data.get("datacontent", {}))
        if pause:
            time.sleep(pause)
    if not merged["datacontent"]:
        raise ValueError(f"no datacontent returned for var {var} over {th_ids}")
    return merged


def series_from_var(
    domain: str,
    var: int,
    *,
    key: str | None = None,
    turvar: int | None = None,
    turtahun: int | None = None,
    turvar_prefer: str | None = r"jumlah|total",
    turtahun_prefer: str | None = r"tahunan",
    freq: str = "tahunan",
    satuan: str | None = None,
    max_vervar: int | None = None,
    min_len: int = 8,
) -> list[Series]:
    """End-to-end: fetch one variable's full history → one `Series` per vervar.

    One real series per vertical category (e.g. province). The derived levels
    (turvar / turtahun) collapse to one each: passed explicitly, else auto-picked
    from the payload by label (`turvar_prefer`/`turtahun_prefer` regex → aggregate
    /annual). Series shorter than `min_len` points are dropped (too short for
    trend/segment/anomaly reasoning).
    """
    periods = list_periods(domain, var, key=key)
    if not periods:
        return []
    payload = fetch_var_data(domain, var, [p["th_id"] for p in periods], key=key)
    auto_tv, auto_tt = best_levels(payload, turvar_prefer=turvar_prefer, turtahun_prefer=turtahun_prefer)
    tv = turvar if turvar is not None else auto_tv
    tt = turtahun if turtahun is not None else auto_tt
    log.info("var %s: turvar=%s turtahun=%s", var, tv, tt)
    vervars = payload.get("vervar", [{"val": 0}])
    if max_vervar is not None:
        vervars = vervars[:max_vervar]
    out: list[Series] = []
    for vv in vervars:
        vv_id = int(vv["val"])
        vv_label = str(vv.get("label") or vv_id)
        try:
            s = build_series(payload, vervar=vv_id, turvar=tv, turtahun=tt, freq=freq)
        except ValueError as e:
            log.warning("skip vervar %s: %s", vv_id, e)
            continue
        if satuan:
            s.satuan = satuan
        if len(s.nilai) < min_len:
            log.info("skip short series vervar %s (n=%d)", vv_id, len(s.nilai))
            continue
        # Prefix the province/category so distinct real series get distinct names.
        s.nama = f"{_slug(vv_label)}_{s.nama}"[:80]
        out.append(s)
    return out


if __name__ == "__main__":  # pragma: no cover
    import argparse

    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Fetch one BPS variable -> Series JSONL")
    ap.add_argument("--domain", default="0000")
    ap.add_argument("--var", type=int, required=True)
    ap.add_argument("--turvar", type=int, default=None)
    ap.add_argument("--turtahun", type=int, default=None)
    ap.add_argument("--freq", default="tahunan")
    ap.add_argument("--out", default="data/raw/bps.jsonl")
    args = ap.parse_args()
    series = series_from_var(
        args.domain, args.var, turvar=args.turvar, turtahun=args.turtahun, freq=args.freq
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    write_series_jsonl(args.out, series)
    log.info("wrote %d series to %s", len(series), args.out)
