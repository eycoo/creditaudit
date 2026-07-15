"""Sintesis reasoning acuan F2-02 — pertanyaan + jawaban gold + rantai operasi
TERPENDEK yang tiap angkanya lolos verifier (grounding 100% by construction).

Masukan : data/processed/benchmark_uji.jsonl (18 Series dari F2-01).
Keluaran: data/processed/benchmark_acuan.jsonl (Sample lengkap: pertanyaan konkret,
          reasoning operasi-form, jawaban gold) + manifest yang di-commit.

Semantik operasi FINAL mengikuti docs/adr/0003:
- `bandingkan_segmen(r1, r2)` = mean(r2) − mean(r1), skalar (Item 2A).
- `z_score(x, pop)` ddof=0; **populasi baseline eksplisit** pada deret bertren
  (Item 3C) supaya anomali tak terdilusi oleh tren.
- Komposisi via `langkah{N}` skalar saja (Item 4A) — di sini rantai pendek,
  tak dipakai.
- `deteksi_anomali` (non-skalar, grounding-nya urusan F1-05) **dihindari**;
  anomali diekspresikan lewat `z_score` skalar agar tergrounding penuh.

Rantai per jenis tugas = rantai *minimal-cukup* (brief v2 §4.2): tiap langkah
angkanya dipakai jawaban; membuang langkah mana pun mematahkan grounding atau
kecukupan.

Jalankan: python scripts/synthesize_reasoning_acuan.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from curate_benchmark_uji import ANOMALI, PENJELASAN, SEGMEN, TREN, CURATION  # noqa: E402
from gearts.schema import Jawaban, ReasoningStep, Sample  # noqa: E402
from gearts.verifier import eval_step, verify_sample  # noqa: E402

TASK_OF = {m["id"]: m["task"] for m in CURATION.values()}
DIFF_OF = {m["id"]: m["difficulty"] for m in CURATION.values()}
ROUND = 3  # desimal `hasil`; jauh di dalam toleransi 0.01/0.01 → selalu grounded

# Titik anomali + jendela populasi baseline per deret anomali (indeks 0-based).
# baseline eksplisit dipakai pada deret bertren (ADR-0003 Item 3C); None = seluruh
# deret (deret volatil-stasioner seperti inflasi).
ANOMALI_PARAMS = {
    "uji_kesehatan_harapan_hidup": dict(idx=51, base="nilai[44:50]", peristiwa="penurunan masa pandemi COVID-19"),
    "uji_kesehatan_imunisasi_campak": dict(idx=38, base="nilai[30:37]", peristiwa="penurunan cakupan masa pandemi COVID-19"),
    "uji_kesehatan_belanja_kesehatan": dict(idx=21, base="nilai[14:20]", peristiwa="lonjakan belanja masa pandemi COVID-19"),
    "uji_pangan_inflasi": dict(idx=28, base=None, peristiwa="hiperinflasi krisis moneter 1998"),
}


def _subjek(sample: Sample) -> str:
    return sample.series.nama.replace("_", " ")


def _step(langkah: int, operasi: str, series: np.ndarray, bindings: dict, teks: str) -> ReasoningStep:
    """Bangun satu langkah: hasil dihitung verifier -> grounded by construction."""
    expected = eval_step(operasi, series, bindings)
    val = round(float(expected), ROUND)
    bindings[f"langkah{langkah}"] = float(expected)  # verifier meng-bind nilai recompute
    return ReasoningStep(langkah=langkah, operasi=operasi, hasil=val, teks=teks)


def _keyakinan(frac: float) -> str:
    if frac >= 0.30:
        return "tinggi"
    if frac >= 0.05:
        return "sedang"
    return "rendah"


def build_reference(sample: Sample, task: str) -> tuple[str, list[ReasoningStep], Jawaban, list[int]]:
    """-> (pertanyaan konkret, reasoning, jawaban gold, indeks langkah yang dikutip jawaban)."""
    v = np.asarray(sample.series.nilai, dtype=float)
    n = len(v)
    subj = _subjek(sample)
    b: dict = {}

    if task == TREN:
        q = f"Bagaimana kecenderungan (tren) {subj} sepanjang periode?"
        s1 = _step(1, f"slope(nilai[0:{n}])", v, b, f"kemiringan tren linear {subj}")
        total = s1.hasil * (n - 1)
        frac = abs(total) / abs(np.mean(v)) if np.mean(v) else 0.0
        if frac < 0.05:
            label = "relatif_stabil"
        else:
            label = "meningkat" if s1.hasil > 0 else "menurun"
        return q, [s1], Jawaban(label=label, keyakinan=_keyakinan(frac)), [1]

    if task == SEGMEN:
        h = n // 2
        q = (f"Bandingkan rata-rata {subj} paruh awal versus paruh akhir periode: "
             f"mana lebih tinggi dan berapa selisihnya?")
        s1 = _step(1, f"bandingkan_segmen(nilai[0:{h}], nilai[{h}:{n}])", v, b,
                   f"selisih rata-rata paruh akhir dikurangi paruh awal {subj}")
        mean_first = float(np.mean(v[:h]))
        frac = abs(s1.hasil) / abs(mean_first) if mean_first else 0.0
        if frac < 0.05:
            label = "setara"
        else:
            label = "paruh_akhir_lebih_tinggi" if s1.hasil > 0 else "paruh_awal_lebih_tinggi"
        return q, [s1], Jawaban(label=label, keyakinan=_keyakinan(frac)), [1]

    if task == ANOMALI:
        p = ANOMALI_PARAMS[sample.id]
        idx, base = p["idx"], p["base"]
        q = f"Apakah terdapat tahun dengan {subj} yang menyimpang tak biasa dari pola di sekitarnya?"
        op = f"z_score(nilai[{idx}], {base})" if base else f"z_score(nilai[{idx}])"
        s1 = _step(1, op, v, b, f"z-score titik dugaan anomali ({p['peristiwa']}) terhadap baseline")
        az = abs(s1.hasil)
        label = "ada_anomali" if az > 3 else "tidak_ada_anomali"
        keyakinan = "tinggi" if az >= 5 else ("sedang" if az >= 3 else "rendah")
        return q, [s1], Jawaban(label=label, keyakinan=keyakinan), [1]

    if task == PENJELASAN:
        # Label komposit yang SELALU butuh kedua langkah (rantai 2 minimal-cukup):
        # arah dari slope (langkah 1), kelas besaran dari persen_naik (langkah 2).
        # Bila arah tren linear & perubahan ujung-ke-ujung berlawanan tanda -> deret
        # tak-monoton (butuh kedua angka untuk terlihat). Menghindari label yang
        # kontradiktif seperti "turun" padahal ujung akhir lebih tinggi.
        q = f"Jelaskan pola utama {subj} sepanjang periode beserta arah dan besar perubahannya."
        s1 = _step(1, f"slope(nilai[0:{n}])", v, b, f"arah & laju tren linear {subj}")
        s2 = _step(2, f"persen_naik(nilai[0]->nilai[{n - 1}])", v, b,
                   f"perubahan total {subj} dari awal ke akhir periode (persen)")
        slope_up, pct = s1.hasil > 0, s2.hasil
        if slope_up != (pct > 0):
            label, keyakinan = "tidak_monoton", "rendah"
        else:
            arah = "naik" if slope_up else "turun"
            besar = "besar" if abs(pct) >= 20 else "kecil"
            label, keyakinan = f"{arah}_{besar}", _keyakinan(abs(pct) / 100.0)
        return q, [s1, s2], Jawaban(label=label, keyakinan=keyakinan), [1, 2]

    raise ValueError(f"jenis tugas tak dikenal: {task}")


def synthesize(sample: Sample) -> tuple[Sample, dict]:
    q, reasoning, jawaban, cites = build_reference(sample, TASK_OF[sample.id])
    full = Sample(id=sample.id, series=sample.series, konteks=sample.konteks,
                  pertanyaan=q, reasoning=reasoning, jawaban=jawaban)
    row = dict(id=sample.id, task=TASK_OF[sample.id], difficulty=DIFF_OF[sample.id],
               n_langkah=len(reasoning), cites=cites,
               chain=" ; ".join(s.operasi for s in reasoning),
               label=jawaban.label, keyakinan=jawaban.keyakinan, pertanyaan=q)
    return full, row


def render_manifest(rows: list[dict]) -> str:
    lines = [
        "# Manifest — Reasoning Acuan Benchmark Uji (F2-02)",
        "",
        "Jawaban gold + rantai operasi acuan **terpendek** untuk 18 deret uji (F2-01).",
        "Data JSONL: `data/processed/benchmark_acuan.jsonl` (gitignored); regen dengan",
        "`python scripts/synthesize_reasoning_acuan.py`.",
        "",
        "Semantik operasi mengikuti **ADR-0003** (final). Tiap sampel **100% grounded**",
        "oleh konstruksi: `hasil` tiap langkah dihitung verifier lalu diverifikasi ulang.",
        "Rantai = *minimal-cukup* (brief v2 §4.2): tiap langkah dikutip jawaban.",
        "",
        f"**Jumlah:** {len(rows)} sampel. Semua `grounding_score = 100.0`.",
        "",
        "| id | tugas | kesulitan | #langkah | rantai operasi | label gold | keyakinan |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['id']} | {r['task']} | {r['difficulty']} | {r['n_langkah']} "
                     f"| `{r['chain']}` | {r['label']} | {r['keyakinan']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    from gearts.schema import read_jsonl, write_jsonl
    src = _ROOT / "data" / "processed" / "benchmark_uji.jsonl"
    out = _ROOT / "data" / "processed" / "benchmark_acuan.jsonl"
    manifest = _ROOT / "data" / "manifest_benchmark_acuan.md"
    if not src.exists():
        print(f"GAGAL: {src} tak ada (jalankan F2-01 dulu).", file=sys.stderr)
        return 1

    samples, rows, bad = [], [], []
    for s in read_jsonl(src):
        full, row = synthesize(s)
        score = verify_sample(full)["grounding_score"]
        if score != 100.0:
            bad.append((s.id, score))
        samples.append(full)
        rows.append(row)

    if bad:
        print(f"GAGAL: {len(bad)} sampel tidak 100% grounded: {bad}", file=sys.stderr)
        return 1

    write_jsonl(out, samples)
    manifest.write_text(render_manifest(rows), encoding="utf-8")
    print(f"OK: {len(samples)} sampel acuan (semua 100% grounded) -> {out}")
    print(f"    panjang rantai: {sorted({r['n_langkah'] for r in rows})}; "
          f"tugas: {sorted({r['task'] for r in rows})}")
    print(f"    manifest -> {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
