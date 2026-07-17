"""Qwen2.5-7B-Instruct adapter via **vLLM offline** (RQ1/RQ2, no fine-tune).

Elicits operation-form reasoning from a stock instruct model so the harness can
re-verify it (ADR-0001/0002: the model proposes operations, the verifier owns the
numbers). Two halves:

- **Pure, import-safe helpers** — `build_prompt` and `parse_model_output` — carry
  all the logic worth testing and need no vLLM/GPU. `parse_model_output` is
  deliberately forgiving: malformed or empty steps are skipped, never fatal.
- **`QwenVLLMAdapter.predict`** — wires prompt → `LLM.generate` → parser. vLLM is
  imported **lazily inside `predict`**, so this module imports and tests offline.

Reasoning length — the RQ2 knob — is controlled two ways: `mode` ("pendek"/
"panjang") changes the prompt instruction, and `max_steps` caps how many parsed
steps are kept. Sweeping these (see `experiments/exp2_rq2.py`) traces the
grounding-vs-token curve.

Two more knobs drive RQ3/RQ4 (`experiments/methods.py`): `prompt_style="prosa"`
elicits free-prose reasoning with no operation format (the B1 / −operation-format
baseline — 0 grounding by construction), and `lora_path` serves a fine-tuned LoRA
adapter on top of the base model (method "Kami" / the −fine-tune contrast). A LoRA
is applied per request, so base and LoRA methods share one loaded engine.
"""
from __future__ import annotations

import re

from gearts.operations import REGISTRY
from gearts.schema import ReasoningStep, Sample

MODEL_DEFAULT = "Qwen/Qwen2.5-7B-Instruct"

# One vLLM engine per (model, kwargs). Adapters that differ only in reasoning
# length (mode/max_steps are prompt/parse-time knobs, same weights) then share a
# single loaded engine — critical so exp2's 4 length settings don't load the 7B
# model 4× and OOM. Keyed on the GPU-affecting config only.
_ENGINE_CACHE: dict = {}

# Stable unique int id per distinct LoRA adapter path — vLLM's LoRARequest needs
# one. Base-model and LoRA methods sharing an `enable_lora` engine differ only by
# the per-request LoRA, so the LoRA is NOT part of the engine cache key.
_LORA_IDS: dict = {}

_OPS = ", ".join(REGISTRY)  # canonical operation names for the prompt

_SYSTEM = (
    "Anda penalar deret waktu yang teliti. Setiap klaim numerik HARUS berbentuk "
    "operasi dari pustaka yang diberikan, dihitung dari deret asli, sehingga bisa "
    "diverifikasi ulang. Jangan mengarang angka."
)

# Free-prose baseline (RQ3 B1 / RQ4 −operation-format): reasoning in plain natural
# language, NO operation format — so nothing is machine-verifiable and grounding
# falls to 0 by construction. A neutral system; the operation-form _SYSTEM would
# contradict the prose instruction.
_SYSTEM_PROSA = (
    "Anda penalar deret waktu. Jelaskan penalaran Anda dengan ringkas dalam bahasa "
    "alami, lalu beri jawaban akhir."
)

# Some instruct models (Gemma) ship a chat template that rejects a "system" role;
# fold the system instruction into the user turn for those instead.
_NO_SYSTEM_ROLE = ("gemma",)

# Instruksi panjang penalaran — knob RQ2.
_MODE_INSTRUKSI = {
    "pendek": "Gunakan langkah **sesedikit mungkin** — hanya operasi yang benar-benar menentukan jawaban.",
    "panjang": "Uraikan penalaran **selengkap mungkin**: tiap pola yang relevan jadi satu langkah operasi.",
}

_FORMAT = (
    "Format keluaran WAJIB, satu langkah per baris:\n"
    "LANGKAH <n>: <operasi> = <hasil> | <penjelasan singkat>\n"
    "diakhiri satu baris:\n"
    "JAWABAN: <label>\n"
    "Acuan indeks: `nilai[i]` satu titik, `nilai[a:b]` irisan (b eksklusif), "
    "`nilai[i]->nilai[j]` pasangan untuk delta/persen_naik.\n"
    f"Operasi yang boleh dipakai: {_OPS}."
)

# LANGKAH 2: persen_naik(nilai[11]->nilai[15]) = 105.3 | naik tajam
_STEP_RE = re.compile(
    r"^\s*LANGKAH\s*\d+\s*:\s*(?P<op>.+?)\s*=\s*(?P<val>-?\d+(?:\.\d+)?)\s*(?:\|\s*(?P<teks>.*))?$",
    re.IGNORECASE,
)
_ANS_RE = re.compile(r"^\s*JAWABAN\s*:\s*(?P<label>.+?)\s*$", re.IGNORECASE)

# Closed answer-label sets per task type (mirror scripts/synthesize_reasoning_acuan.py).
# The prompt MUST present these or the model can't produce the exact gold token and
# answer_accuracy is 0 by construction.
# ponytail: infer task from the templated question; move to an explicit
# `opsi_jawaban` field when the benchmark is regenerated.
_TASK_OPSI = {
    "tren": ["meningkat", "menurun", "relatif_stabil"],
    "segmen": ["paruh_awal_lebih_tinggi", "paruh_akhir_lebih_tinggi", "setara"],
    "anomali": ["ada_anomali", "tidak_ada_anomali"],
    "penjelasan": ["naik_besar", "naik_kecil", "turun_besar", "turun_kecil", "tidak_monoton"],
}

# One worked example — instruct models follow the LANGKAH/JAWABAN format far more
# reliably when shown it once than when only told the grammar.
_CONTOH = (
    "Contoh format (deret lain, nilai = [10, 12, 15, 19]):\n"
    "LANGKAH 1: slope(nilai[0:4]) = 3.0 | tren naik linear\n"
    "LANGKAH 2: persen_naik(nilai[0]->nilai[3]) = 90.0 | perubahan ujung ke ujung\n"
    "JAWABAN: naik_besar"
)


def answer_options(sample: Sample) -> list[str]:
    """Allowed answer labels for this item, inferred from the templated question."""
    q = sample.pertanyaan.lower()
    if "paruh awal" in q or "paruh akhir" in q:
        return _TASK_OPSI["segmen"]
    if "menyimpang" in q or "anomali" in q:
        return _TASK_OPSI["anomali"]
    if "pola utama" in q or "arah dan besar" in q:
        return _TASK_OPSI["penjelasan"]
    if "kecenderungan" in q or "tren" in q:
        return _TASK_OPSI["tren"]
    return []


def _fmt_series(sample: Sample) -> str:
    vals = ", ".join(str(v) for v in sample.series.nilai)
    return f"[{vals}]"


def build_prompt(sample: Sample, mode: str = "panjang", max_steps: int | None = None,
                 opsi: list[str] | None = None) -> str:
    """User prompt for one item. Pure — no model call, safe to test offline."""
    instruksi = _MODE_INSTRUKSI.get(mode, _MODE_INSTRUKSI["panjang"])
    if max_steps is not None:
        instruksi += f" Pakai paling banyak {max_steps} langkah."
    opsi = answer_options(sample) if opsi is None else opsi
    menu = f"JAWABAN harus **tepat satu** dari label ini: {', '.join(opsi)}.\n" if opsi else ""
    return (
        f"Deret: {sample.series.nama} (satuan {sample.series.satuan}, {sample.series.freq}).\n"
        f"Konteks: {sample.konteks}\n"
        f"nilai = {_fmt_series(sample)}\n"
        f"Pertanyaan: {sample.pertanyaan}\n\n"
        f"{instruksi}\n{menu}{_FORMAT}\n\n{_CONTOH}"
    )


_FORMAT_PROSA = (
    "Jelaskan penalaran Anda dalam bahasa alami (prosa biasa), lalu akhiri dengan "
    "tepat satu baris:\n"
    "JAWABAN: <label>"
)


def build_prompt_prosa(sample: Sample, opsi: list[str] | None = None) -> str:
    """Free-prose prompt (RQ3 B1 / RQ4 ablation): natural-language reasoning, **no**
    operation format. Pure. The verifier finds no operation steps → grounding 0; the
    final `JAWABAN:` line still lets answer accuracy be scored."""
    opsi = answer_options(sample) if opsi is None else opsi
    menu = f"JAWABAN harus **tepat satu** dari label ini: {', '.join(opsi)}.\n" if opsi else ""
    return (
        f"Deret: {sample.series.nama} (satuan {sample.series.satuan}, {sample.series.freq}).\n"
        f"Konteks: {sample.konteks}\n"
        f"nilai = {_fmt_series(sample)}\n"
        f"Pertanyaan: {sample.pertanyaan}\n\n"
        f"{menu}{_FORMAT_PROSA}"
    )


def _normalize_label(s: str) -> str:
    return s.strip().strip(".").lower()


def _canon(s: str) -> str:
    """Collapse to a comparable slug: lowercase, non-alphanumerics → underscore."""
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def snap_label(label: str, opsi: list[str]) -> str:
    """Snap a free-form label onto the closed option set (spacing/verbosity tolerant).

    `"paruh awal lebih tinggi"` → `"paruh_awal_lebih_tinggi"`, `"tren menurun"` →
    `"menurun"`. Returns the label unchanged if nothing matches (or no options).
    """
    if not opsi:
        return label
    c = _canon(label)
    for o in opsi:
        if _canon(o) == c:
            return o
    for o in opsi:  # verbose answer that contains an option token
        if _canon(o) in c:
            return o
    return label


def parse_model_output(text: str) -> tuple[list[ReasoningStep], str]:
    """Parse raw model text → (reasoning steps, answer label). Forgiving.

    Only lines matching the LANGKAH format become steps; anything else (prose,
    code fences, blank lines) is ignored. A step whose operation lacks a call
    `(...)` or whose value is unparseable is skipped rather than raising. Steps
    are renumbered 1..N so verifier `langkah{n}` bindings stay consistent.
    """
    steps: list[ReasoningStep] = []
    label = ""
    for line in text.splitlines():
        m_ans = _ANS_RE.match(line)
        if m_ans:
            label = _normalize_label(m_ans.group("label"))
            continue
        m = _STEP_RE.match(line)
        if not m:
            continue
        op = m.group("op").strip()
        if "(" not in op or ")" not in op:  # not an operation call → skip prose
            continue
        try:
            hasil = float(m.group("val"))
        except ValueError:
            continue
        teks = (m.group("teks") or "").strip()
        steps.append(ReasoningStep(langkah=len(steps) + 1, operasi=op, hasil=hasil, teks=teks))
    return steps, label


def build_chat(model: str, system: str, prompt: str) -> list[dict]:
    """Chat messages for `model` — folds system→user when the model's template
    rejects a system role (e.g. Gemma), else a normal system+user pair. Pure."""
    if any(t in model.lower() for t in _NO_SYSTEM_ROLE):
        return [{"role": "user", "content": f"{system}\n\n{prompt}"}]
    return [{"role": "system", "content": system}, {"role": "user", "content": prompt}]


class QwenVLLMAdapter:
    """`ModelAdapter` for Qwen2.5-7B-Instruct on vLLM (offline / single-node GPU).

    vLLM is loaded lazily on first `predict`; constructing the adapter costs
    nothing and needs no GPU.
    """

    def __init__(
        self,
        name: str | None = None,
        model: str = MODEL_DEFAULT,
        mode: str = "panjang",
        max_steps: int | None = None,
        max_tokens: int = 512,
        temperature: float = 0.0,
        prompt_style: str = "operasi",
        system: str | None = None,
        lora_path: str | None = None,
        lora_name: str = "penalar_ts",
        **llm_kwargs,
    ):
        self.model = model
        self.mode = mode
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.prompt_style = prompt_style  # "operasi" (LANGKAH format) | "prosa" (free prose)
        self.system = system or (_SYSTEM_PROSA if prompt_style == "prosa" else _SYSTEM)
        self.lora_path = lora_path  # fine-tuned adapter dir; None → base model
        self.lora_name = lora_name
        # Serving a LoRA: the engine must be built with enable_lora and a max rank
        # ≥ the adapter's r (ours is 32; vLLM defaults to 16). Folding these into
        # the engine kwargs means base-model and LoRA methods that pass the SAME
        # kwargs (see experiments/methods.lora_engine_kwargs) land on ONE cached
        # engine — the LoRA is selected per request, not per engine.
        if lora_path:
            llm_kwargs = {**llm_kwargs, "enable_lora": True,
                          "max_lora_rank": max(32, int(llm_kwargs.get("max_lora_rank", 0)))}
        self._llm_kwargs = llm_kwargs
        self.name = name or self._default_name()
        self._llm = None
        self._SamplingParams = None
        self._lora_req = None
        self.last_raw = ""  # last raw model text, for debug_dump.py

    def _default_name(self) -> str:
        base = f"qwen2.5-7b:{self.mode}" + (f":<= {self.max_steps}" if self.max_steps else "")
        if self.prompt_style == "prosa":
            base += ":prosa"
        if self.lora_path:
            base += ":lora"
        return base

    def _ensure_llm(self):
        if self._llm is None:
            key = (self.model, tuple(sorted(self._llm_kwargs.items())))
            entry = _ENGINE_CACHE.get(key)
            if entry is None:  # first adapter with this config actually loads the model
                try:
                    from vllm import LLM, SamplingParams  # lazy: only when actually running a model
                except ImportError as e:  # pragma: no cover - exercised only off-GPU
                    raise RuntimeError(
                        "vLLM tidak terpasang. Jalankan di lingkungan ber-GPU: `pip install vllm` "
                        "(lihat experiments/README-kaggle.md)."
                    ) from e
                entry = (LLM(model=self.model, **self._llm_kwargs), SamplingParams)
                _ENGINE_CACHE[key] = entry
            self._llm, self._SamplingParams = entry
        return self._llm

    def _lora_request(self):  # pragma: no cover - needs vLLM
        """LoRARequest for this adapter's fine-tuned weights, or None for the base
        model. Cached; each distinct adapter path keeps a stable unique int id."""
        if not self.lora_path:
            return None
        if self._lora_req is None:
            from vllm.lora.request import LoRARequest  # lazy: only on the GPU path
            lid = _LORA_IDS.setdefault(self.lora_path, len(_LORA_IDS) + 1)
            self._lora_req = LoRARequest(self.lora_name, lid, self.lora_path)
        return self._lora_req

    def _generate(self, prompt: str) -> str:  # pragma: no cover - needs GPU
        llm = self._ensure_llm()
        sp = self._SamplingParams(temperature=self.temperature, max_tokens=self.max_tokens)
        convo = build_chat(self.model, self.system, prompt)
        lreq = self._lora_request()
        out = llm.chat(convo, sp, lora_request=lreq) if lreq is not None else llm.chat(convo, sp)
        return out[0].outputs[0].text

    def predict(self, sample: Sample) -> tuple[list[ReasoningStep], str]:
        if self.prompt_style == "prosa":
            prompt = build_prompt_prosa(sample)
        else:
            prompt = build_prompt(sample, mode=self.mode, max_steps=self.max_steps)
        text = self._generate(prompt)
        self.last_raw = text
        steps, label = parse_model_output(text)
        label = snap_label(label, answer_options(sample))  # onto closed option set
        if self.max_steps is not None and len(steps) > self.max_steps:
            steps = steps[: self.max_steps]
            for i, s in enumerate(steps, start=1):
                s.langkah = i
        return steps, label
