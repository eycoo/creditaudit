"""Kurasi benchmark uji F2-01 — deret time series *real* dari sumber publik.

Menghasilkan `Sample` JSONL (series + stub konteks/pertanyaan, **tanpa reasoning**;
reasoning & jawaban gold diisi F2-02) plus manifest yang di-commit.

Sumber data: World Bank Open Data API untuk Indonesia (IDN). World Bank
menerbitkan ulang data resmi Indonesia (BPS, Kemenkes→WHO), dapat diambil
sebagai angka *eksak* lewat API — dipilih di atas dashboard PIHPS/Kemenkes yang
hanya melayani PDF/param-API sehingga angka eksak sulit diambil andal.

Anti-bocor (brief §9.4): sumber & granularitas ini (agregat tahunan World Bank)
**berbeda** dari sumber train yang direncanakan (scrape harian PIHPS, mingguan
Kemenkes SKDR, BMKG). Deret ini **khusus uji** — jangan dipakai di train.

Pipeline dua tahap (network di-sandbox): `scripts/fetch_wb.ps1` menyimpan JSON
mentah ke data/raw/ (gitignored); skrip ini membangun Sample dari file mentah itu
— tanpa network, deterministik, bisa diuji.

Jalankan:  python scripts/curate_benchmark_uji.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from gearts.schema import Jawaban, Sample, Series, write_jsonl  # noqa: E402

RETRIEVAL_DATE = "2026-07-15"
WB_URL = "https://api.worldbank.org/v2/country/IDN/indicator/{code}?format=json&per_page=300&date=1970:2024"

# Empat jenis tugas penalaran (CONTEXT.md / brief §6).
ANOMALI = "anomali"          # indikasi anomali / outbreak
TREN = "tren"                # karakterisasi tren
SEGMEN = "segmen"            # perbandingan segmen
PENJELASAN = "penjelasan"    # penjelasan pola

_STUB = {
    ANOMALI: "Apakah terdapat tahun dengan anomali (lonjakan atau penurunan tak biasa) pada deret ini?",
    TREN: "Bagaimana karakterisasi tren deret ini sepanjang periode?",
    SEGMEN: "Bandingkan rata-rata paruh awal dengan paruh akhir periode: mana lebih tinggi dan seberapa besar selisihnya?",
    PENJELASAN: "Jelaskan pola utama yang terlihat pada deret ini beserta kemungkinan penyebabnya.",
}

# Kurasi manual: tiap deret real diberi domain, jenis tugas, tingkat kesulitan,
# konteks, dan satuan. `id` unik; `pertanyaan` memakai stub jenis tugas (F2-02
# menyempurnakan). Kesulitan bervariasi: deret tren-jelas = easy; deret
# bising/nyaris-datar/ada distraktor = hard.
CURATION: dict[str, dict] = {
    # --- Domain: kesehatan ---
    "SH.DYN.MORT": dict(id="uji_kesehatan_mortalitas_balita", domain="kesehatan",
        nama="mortalitas_balita", satuan="per 1000 kelahiran hidup", freq="tahunan",
        task=TREN, difficulty="easy",
        konteks="Angka kematian balita (bawah lima tahun) Indonesia per 1000 kelahiran hidup, tahunan."),
    "SP.DYN.IMRT.IN": dict(id="uji_kesehatan_mortalitas_bayi", domain="kesehatan",
        nama="mortalitas_bayi", satuan="per 1000 kelahiran hidup", freq="tahunan",
        task=SEGMEN, difficulty="easy",
        konteks="Angka kematian bayi Indonesia per 1000 kelahiran hidup, tahunan."),
    "SP.DYN.LE00.IN": dict(id="uji_kesehatan_harapan_hidup", domain="kesehatan",
        nama="harapan_hidup", satuan="tahun", freq="tahunan",
        task=ANOMALI, difficulty="medium",
        konteks="Angka harapan hidup saat lahir Indonesia (tahun), tahunan; ada penurunan di masa pandemi."),
    "SH.STA.MMRT": dict(id="uji_kesehatan_mortalitas_ibu", domain="kesehatan",
        nama="mortalitas_ibu", satuan="per 100000 kelahiran hidup", freq="tahunan",
        task=TREN, difficulty="easy",
        konteks="Rasio kematian ibu Indonesia per 100000 kelahiran hidup, tahunan."),
    "SH.IMM.MEAS": dict(id="uji_kesehatan_imunisasi_campak", domain="kesehatan",
        nama="imunisasi_campak", satuan="persen anak", freq="tahunan",
        task=ANOMALI, difficulty="medium",
        konteks="Cakupan imunisasi campak anak usia 12-23 bulan Indonesia (persen), tahunan; fluktuatif."),
    "SH.IMM.IDPT": dict(id="uji_kesehatan_imunisasi_dpt", domain="kesehatan",
        nama="imunisasi_dpt", satuan="persen anak", freq="tahunan",
        task=PENJELASAN, difficulty="medium",
        konteks="Cakupan imunisasi DPT3 anak usia 12-23 bulan Indonesia (persen), tahunan."),
    "SH.TBS.INCD": dict(id="uji_kesehatan_insiden_tbc", domain="kesehatan",
        nama="insiden_tbc", satuan="per 100000 penduduk", freq="tahunan",
        task=TREN, difficulty="hard",
        konteks="Insiden tuberkulosis Indonesia per 100000 penduduk, tahunan; perubahan lambat/ambigu."),
    "SH.DYN.NMRT": dict(id="uji_kesehatan_mortalitas_neonatal", domain="kesehatan",
        nama="mortalitas_neonatal", satuan="per 1000 kelahiran hidup", freq="tahunan",
        task=SEGMEN, difficulty="easy",
        konteks="Angka kematian neonatal Indonesia per 1000 kelahiran hidup, tahunan."),
    "SH.XPD.CHEX.GD.ZS": dict(id="uji_kesehatan_belanja_kesehatan", domain="kesehatan",
        nama="belanja_kesehatan", satuan="persen PDB", freq="tahunan",
        task=ANOMALI, difficulty="hard",
        konteks="Belanja kesehatan Indonesia sebagai persen PDB, tahunan; bising dengan lonjakan masa pandemi."),
    # --- Domain: pangan-pertanian ---
    "AG.PRD.FOOD.XD": dict(id="uji_pangan_indeks_produksi_pangan", domain="pangan-pertanian",
        nama="indeks_produksi_pangan", satuan="indeks (2014-2016=100)", freq="tahunan",
        task=TREN, difficulty="easy",
        konteks="Indeks produksi pangan Indonesia (2014-2016=100), tahunan."),
    "AG.PRD.CROP.XD": dict(id="uji_pangan_indeks_produksi_tanaman", domain="pangan-pertanian",
        nama="indeks_produksi_tanaman", satuan="indeks (2014-2016=100)", freq="tahunan",
        task=PENJELASAN, difficulty="medium",
        konteks="Indeks produksi tanaman pangan Indonesia (2014-2016=100), tahunan; ada dip antar-tahun."),
    "AG.YLD.CREL.KG": dict(id="uji_pangan_hasil_serealia", domain="pangan-pertanian",
        nama="hasil_serealia", satuan="kg per hektar", freq="tahunan",
        task=TREN, difficulty="easy",
        konteks="Hasil (yield) serealia Indonesia kg per hektar, tahunan."),
    "NV.AGR.TOTL.ZS": dict(id="uji_pangan_pdb_pertanian", domain="pangan-pertanian",
        nama="pangsa_pdb_pertanian", satuan="persen PDB", freq="tahunan",
        task=SEGMEN, difficulty="medium",
        konteks="Nilai tambah sektor pertanian Indonesia sebagai persen PDB, tahunan; pangsa menurun."),
    "AG.LND.AGRI.ZS": dict(id="uji_pangan_lahan_pertanian", domain="pangan-pertanian",
        nama="lahan_pertanian", satuan="persen luas lahan", freq="tahunan",
        task=TREN, difficulty="hard",
        konteks="Luas lahan pertanian Indonesia sebagai persen total lahan, tahunan; nyaris datar/ambigu."),
    "FP.CPI.TOTL.ZG": dict(id="uji_pangan_inflasi", domain="pangan-pertanian",
        nama="inflasi_tahunan", satuan="persen", freq="tahunan",
        task=ANOMALI, difficulty="medium",
        konteks="Inflasi harga konsumen Indonesia (persen per tahun), tahunan; volatil dengan lonjakan."),
    "FP.CPI.TOTL": dict(id="uji_pangan_indeks_harga_konsumen", domain="pangan-pertanian",
        nama="indeks_harga_konsumen", satuan="indeks (2010=100)", freq="tahunan",
        task=TREN, difficulty="easy",
        konteks="Indeks harga konsumen Indonesia (2010=100), tahunan; naik konsisten."),
    "AG.LND.ARBL.ZS": dict(id="uji_pangan_lahan_subur", domain="pangan-pertanian",
        nama="lahan_subur", satuan="persen luas lahan", freq="tahunan",
        task=PENJELASAN, difficulty="hard",
        konteks="Luas lahan subur (arable) Indonesia sebagai persen total lahan, tahunan; perubahan lambat."),
    "SL.AGR.EMPL.ZS": dict(id="uji_pangan_tenaga_kerja_pertanian", domain="pangan-pertanian",
        nama="tenaga_kerja_pertanian", satuan="persen tenaga kerja", freq="tahunan",
        task=SEGMEN, difficulty="medium",
        konteks="Pangsa tenaga kerja di sektor pertanian Indonesia (persen), tahunan; menurun."),
}


def extract_series(raw_json: list) -> list[tuple[int, float]]:
    """Ambil (tahun, nilai) non-null dari respons World Bank, urut menaik."""
    if not (isinstance(raw_json, list) and len(raw_json) == 2 and raw_json[1]):
        raise ValueError("format respons World Bank tak dikenali")
    pts = [(int(row["date"]), float(row["value"]))
           for row in raw_json[1] if row.get("value") is not None]
    return sorted(pts, key=lambda t: t[0])


def build_sample(code: str, raw_json: list) -> tuple[Sample, dict]:
    """Bangun satu Sample uji (tanpa reasoning) + baris manifest dari data mentah."""
    meta = CURATION[code]
    pts = extract_series(raw_json)
    if not pts:
        raise ValueError(f"{code}: tak ada titik non-null")
    years = [y for y, _ in pts]
    sample = Sample(
        id=meta["id"],
        series=Series(nama=meta["nama"], satuan=meta["satuan"],
                      freq=meta["freq"], nilai=[v for _, v in pts]),
        konteks=meta["konteks"],
        pertanyaan=_STUB[meta["task"]],
        reasoning=[],                                # F2-02 mengisi
        jawaban=Jawaban(label="", keyakinan="sedang"),  # stub; gold di F2-02
    )
    row = dict(id=meta["id"], domain=meta["domain"], task=meta["task"],
               difficulty=meta["difficulty"], n=len(pts),
               rentang=f"{years[0]}-{years[-1]}",
               sumber=WB_URL.format(code=code), tanggal_ambil=RETRIEVAL_DATE)
    return sample, row


def curate_all(raw_dir: Path) -> tuple[list[Sample], list[dict]]:
    samples, rows = [], []
    for code in CURATION:
        f = raw_dir / f"wb_{code}.json"
        if not f.exists():
            print(f"LEWAT {code}: {f.name} tidak ada", file=sys.stderr)
            continue
        raw = json.loads(f.read_text(encoding="utf-8"))
        try:
            s, r = build_sample(code, raw)
        except ValueError as e:
            print(f"LEWAT {code}: {e}", file=sys.stderr)
            continue
        problems = s.validate()
        if problems:
            print(f"LEWAT {code}: gagal validasi Series: {problems}", file=sys.stderr)
            continue
        samples.append(s)
        rows.append(r)
    return samples, rows


def render_manifest(rows: list[dict]) -> str:
    lines = [
        "# Manifest — Benchmark Uji (F2-01)",
        "",
        "Deret time series **real, khusus uji** untuk RQ1/RQ2. File data JSONL ada di",
        "`data/processed/benchmark_uji.jsonl` (gitignored); regen dengan",
        "`scripts/fetch_wb.ps1` lalu `python scripts/curate_benchmark_uji.py`.",
        "",
        "**Sumber:** World Bank Open Data API untuk Indonesia (IDN) — penerbitan ulang",
        "data resmi Indonesia (BPS, Kemenkes/WHO). Dipilih karena angkanya *eksak* &",
        "dapat diambil andal via API.",
        "",
        "**Anti-bocor (§9.4):** agregat tahunan World Bank ini berbeda sumber &",
        "granularitas dari sumber train (PIHPS harian, Kemenkes SKDR mingguan, BMKG).",
        "**Khusus uji — jangan dipakai di train.**",
        "",
        f"**Tanggal ambil:** {RETRIEVAL_DATE}. **Jumlah deret:** {len(rows)}.",
        "",
        "| id | domain | tugas | kesulitan | n | rentang | sumber |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['id']} | {r['domain']} | {r['task']} | {r['difficulty']} "
                     f"| {r['n']} | {r['rentang']} | {r['sumber']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    raw_dir = _ROOT / "data" / "raw"
    out_jsonl = _ROOT / "data" / "processed" / "benchmark_uji.jsonl"
    manifest = _ROOT / "data" / "manifest_benchmark_uji.md"
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    samples, rows = curate_all(raw_dir)
    if len(samples) < 15:
        print(f"GAGAL: hanya {len(samples)} deret valid (<15).", file=sys.stderr)
        return 1
    write_jsonl(out_jsonl, samples)
    manifest.write_text(render_manifest(rows), encoding="utf-8")
    tasks = {r["task"] for r in rows}
    print(f"OK: {len(samples)} deret -> {out_jsonl}")
    print(f"    tugas tercakup: {sorted(tasks)}")
    print(f"    manifest -> {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
