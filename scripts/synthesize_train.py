"""Sintesis TRAIN set untuk fine-tune (F4-04).

Deret **terkontrol semi-sintetik** + reasoning operasi-form yang tiap angkanya
dihitung lalu diverifikasi ulang oleh verifier -> **grounding 100% by construction**
(langkah yang tak ground = di-drop, bukan ditulis). Label jawaban DITURUNKAN dari
angka yang sudah grounded, jadi selalu konsisten.

Anti-bocor (brief §9.4): deret train dibangkitkan sintetik pada frekuensi tinggi
(harian/mingguan/bulanan) dengan domain mikro (ritel, energi, cuaca, logistik) —
**berbeda** dari benchmark uji (World Bank tahunan, makro kesehatan/pangan). Tak ada
`id`, nama deret, sumber, maupun granularitas yang sama dengan test.

Semantik operasi mengikuti ADR-0003 (sama seperti synthesize_reasoning_acuan.py):
slope (tren), bandingkan_segmen (segmen), z_score dgn populasi baseline eksplisit
(anomali), slope+persen_naik (penjelasan). Rantai = minimal-cukup.

Keluaran:
- data/synthetic/train_acuan.jsonl   (Sample lengkap)
- data/manifest_train.md

Jalankan: python scripts/synthesize_train.py [N_PER_SEL]   (default 30 -> ~360 item)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
for p in (_ROOT / "src", _ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from gearts.schema import Jawaban, ReasoningStep, Sample, Series, write_jsonl  # noqa: E402
from gearts.verifier import eval_step, verify_sample  # noqa: E402

TREN, SEGMEN, ANOMALI, PENJELASAN = "tren", "segmen", "anomali", "penjelasan"
TASKS = [TREN, SEGMEN, ANOMALI, PENJELASAN]
DIFFS = ["easy", "medium", "hard"]
ROUND = 3

# Nama+satuan deret per frekuensi — mikro/frekuensi-tinggi, sengaja beda dari
# test (WB makro tahunan) untuk anti-bocor.
_POOL = {
    "harian": [("penjualan_eceran", "unit"), ("beban_listrik", "MW"), ("curah_hujan", "mm"),
               ("suhu_udara", "derajat C"), ("pengguna_aktif", "orang"), ("harga_cabai", "rupiah/kg"),
               ("volume_pengiriman", "paket"), ("transaksi_pembayaran", "transaksi")],
    "mingguan": [("kunjungan_pasien", "orang"), ("stok_gudang", "ton"), ("harga_bawang", "rupiah/kg"),
                 ("trafik_situs", "kunjungan"), ("produksi_pabrik", "unit")],
    "bulanan": [("konsumsi_bbm", "kiloliter"), ("okupansi_hotel", "persen"),
                ("pendaftaran_pengguna", "akun"), ("impor_komoditas", "ton")],
}
_LEN = {"harian": [14, 21, 30], "mingguan": [12, 20, 26], "bulanan": [12, 18, 24]}
# Skala derau relatif per kesulitan: easy = sinyal bersih, hard = bising/ambang.
_NOISE = {"easy": 0.02, "medium": 0.06, "hard": 0.14}


def _subjek(nama: str) -> str:
    return nama.replace("_", " ")


def _step(langkah: int, operasi: str, series: np.ndarray, b: dict, teks: str) -> ReasoningStep:
    """Hasil dihitung verifier lalu dibulatkan -> grounded by construction."""
    expected = eval_step(operasi, series, b)
    b[f"langkah{langkah}"] = float(expected)
    return ReasoningStep(langkah=langkah, operasi=operasi, hasil=round(float(expected), ROUND), teks=teks)


def _keyakinan(frac: float) -> str:
    return "tinggi" if frac >= 0.30 else ("sedang" if frac >= 0.05 else "rendah")


# ---------- pembangkit deret terkontrol (semi-sintetik) ----------

def _gen_series(task: str, diff: str, i: int, rng: np.random.Generator) -> tuple[np.ndarray, dict]:
    """-> (nilai, meta) di mana meta membawa parameter yang dibutuhkan builder."""
    noise = _NOISE[diff]
    freq = rng.choice(list(_LEN))
    n = int(rng.choice(_LEN[freq]))
    L = float(rng.uniform(80, 600))
    nama, satuan = _POOL[freq][i % len(_POOL[freq])]
    meta = {"freq": freq, "nama": nama, "satuan": satuan, "n": n}

    if task == TREN:
        arah = (1, -1, 0)[i % 3]                       # naik / turun / datar
        mag = {"easy": 0.9, "medium": 0.4, "hard": 0.12}[diff]
        slope = arah * mag * L / n
        x = np.arange(n)
        v = L + slope * x + rng.normal(0, noise * L, n)

    elif task == SEGMEN:
        n += n % 2                                     # genap
        arah = (1, -1, 0)[i % 3]
        delta = {"easy": 0.35, "medium": 0.15, "hard": 0.04}[diff] * arah
        h = n // 2
        v = np.empty(n)
        v[:h] = rng.normal(L, noise * L, h)
        v[h:] = rng.normal(L * (1 + delta), noise * L, n - h)
        meta["h"] = h

    elif task == ANOMALI:
        k = n - 1                                      # baseline = titik 0..k-1, anomali di k
        s = max(noise, 0.02) * L
        base = rng.normal(L, s, k)
        ada = (i % 2 == 0)
        if ada:
            z = {"easy": 6.5, "medium": 4.5, "hard": 3.4}[diff]
        else:
            z = {"easy": 0.6, "medium": 1.3, "hard": 2.2}[diff]
        z *= (1 if i % 4 < 2 else -1)                  # anomali bisa lonjakan atau penurunan
        anom = float(np.mean(base) + z * np.std(base))
        v = np.append(base, anom)
        meta.update(idx=k, base_lo=0, base_hi=k)

    else:  # PENJELASAN — tren + lengkung (kadang tak-monoton)
        arah = (1, -1)[i % 2]
        mag = {"easy": 0.8, "medium": 0.35, "hard": 0.15}[diff]
        slope = arah * mag * L / n
        curv = 0.0 if i % 3 else (rng.uniform(-1, 1) * 2.5 * L / (n * n))  # 1/3 melengkung
        x = np.arange(n)
        v = L + slope * x + curv * (x - n / 2) ** 2 + rng.normal(0, noise * L, n)

    v = np.clip(v, 1.0, None)                           # jaga positif (persen_naik butuh nilai[0]!=0)
    return np.round(v, 2), meta


# ---------- builder reasoning per tugas (mirror synthesize_reasoning_acuan) ----------

def _build(task: str, sample: Sample, meta: dict) -> tuple[str, list[ReasoningStep], Jawaban, list[int]]:
    v = np.asarray(sample.series.nilai, dtype=float)
    n = len(v)
    subj = _subjek(sample.series.nama)
    b: dict = {}

    if task == TREN:
        q = f"Bagaimana kecenderungan (tren) {subj} sepanjang periode?"
        s1 = _step(1, f"slope(nilai[0:{n}])", v, b, f"kemiringan tren linear {subj}")
        total = s1.hasil * (n - 1)
        frac = abs(total) / abs(np.mean(v)) if np.mean(v) else 0.0
        label = "relatif_stabil" if frac < 0.05 else ("meningkat" if s1.hasil > 0 else "menurun")
        return q, [s1], Jawaban(label, _keyakinan(frac)), [1]

    if task == SEGMEN:
        h = meta["h"]
        q = (f"Bandingkan rata-rata {subj} paruh awal versus paruh akhir periode: "
             f"mana lebih tinggi dan berapa selisihnya?")
        s1 = _step(1, f"bandingkan_segmen(nilai[0:{h}], nilai[{h}:{n}])", v, b,
                   f"selisih rata-rata paruh akhir dikurangi paruh awal {subj}")
        mean_first = float(np.mean(v[:h]))
        frac = abs(s1.hasil) / abs(mean_first) if mean_first else 0.0
        label = "setara" if frac < 0.05 else ("paruh_akhir_lebih_tinggi" if s1.hasil > 0 else "paruh_awal_lebih_tinggi")
        return q, [s1], Jawaban(label, _keyakinan(frac)), [1]

    if task == ANOMALI:
        idx, lo, hi = meta["idx"], meta["base_lo"], meta["base_hi"]
        q = f"Apakah terdapat titik dengan {subj} yang menyimpang tak biasa dari pola di sekitarnya?"
        s1 = _step(1, f"z_score(nilai[{idx}], nilai[{lo}:{hi}])", v, b,
                   f"z-score titik terakhir {subj} terhadap baseline sebelumnya")
        az = abs(s1.hasil)
        label = "ada_anomali" if az > 3 else "tidak_ada_anomali"
        keyakinan = "tinggi" if az >= 5 else ("sedang" if az >= 3 else "rendah")
        return q, [s1], Jawaban(label, keyakinan), [1]

    if task == PENJELASAN:
        q = f"Jelaskan pola utama {subj} sepanjang periode beserta arah dan besar perubahannya."
        s1 = _step(1, f"slope(nilai[0:{n}])", v, b, f"arah & laju tren linear {subj}")
        s2 = _step(2, f"persen_naik(nilai[0]->nilai[{n - 1}])", v, b,
                   f"perubahan total {subj} dari awal ke akhir periode (persen)")
        slope_up, pct = s1.hasil > 0, s2.hasil
        if slope_up != (pct > 0):
            label, keyakinan = "tidak_monoton", "rendah"
        else:
            label = ("naik" if slope_up else "turun") + ("_besar" if abs(pct) >= 20 else "_kecil")
            keyakinan = _keyakinan(abs(pct) / 100.0)
        return q, [s1, s2], Jawaban(label, keyakinan), [1, 2]

    raise ValueError(task)


def synthesize_one(task: str, diff: str, i: int, rng: np.random.Generator):
    v, meta = _gen_series(task, diff, i, rng)
    stub = Sample(id=f"train_{task}_{diff}_{i:03d}",
                  series=Series(nama=meta["nama"], satuan=meta["satuan"], freq=meta["freq"], nilai=v.tolist()),
                  konteks=f"Deret {meta['freq']} {_subjek(meta['nama'])} selama {meta['n']} periode.",
                  pertanyaan="", reasoning=[], jawaban=Jawaban("", "sedang"))
    q, reasoning, jawaban, cites = _build(task, stub, meta)
    full = Sample(id=stub.id, series=stub.series, konteks=stub.konteks,
                  pertanyaan=q, reasoning=reasoning, jawaban=jawaban)
    row = dict(id=full.id, task=task, difficulty=diff, n_langkah=len(reasoning),
               label=jawaban.label, freq=meta["freq"])
    return full, row


def main() -> int:
    n_per = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rng = np.random.default_rng(20260716)
    samples, rows, dropped = [], [], 0
    for task in TASKS:
        for diff in DIFFS:
            for i in range(n_per):
                full, row = synthesize_one(task, diff, i, rng)
                problems = full.validate()
                score = verify_sample(full)["grounding_score"]
                if problems or score != 100.0:       # drop, jangan tulis yang tak bersih
                    dropped += 1
                    continue
                samples.append(full)
                rows.append(row)

    out = _ROOT / "data" / "synthetic" / "train_acuan.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out, samples)

    # distribusi + manifest
    from collections import Counter
    by_task = Counter(r["task"] for r in rows)
    by_diff = Counter(r["difficulty"] for r in rows)
    by_label = Counter(r["label"] for r in rows)
    lines = [
        "# Manifest — Train Set (F4-04)", "",
        "Deret **terkontrol semi-sintetik** + reasoning operasi-form, **100% grounded**",
        "oleh konstruksi (verifier in-the-loop; langkah tak-ground di-drop). Regen dengan",
        "`python scripts/synthesize_train.py`.", "",
        "**Anti-bocor (§9.4):** deret sintetik frekuensi tinggi (harian/mingguan/bulanan),",
        "domain mikro — beda `id`, nama, sumber, & granularitas dari benchmark uji (WB tahunan makro).",
        "**Khusus train — tak beririsan dengan test.**", "",
        f"**Jumlah:** {len(samples)} sampel (drop {dropped}). Semua `grounding_score = 100.0`.", "",
        f"- per tugas: {dict(by_task)}",
        f"- per kesulitan: {dict(by_diff)}",
        f"- per label: {dict(by_label)}", "",
    ]
    (_ROOT / "data" / "manifest_train.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"OK: {len(samples)} sampel train (semua 100% grounded, drop {dropped}) -> {out}")
    print(f"    tugas={dict(by_task)}")
    print(f"    kesulitan={dict(by_diff)}")
    print(f"    label={dict(by_label)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
