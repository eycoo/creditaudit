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

_OPS = ", ".join(REGISTRY)  # canonical operation names for the prompt

_SYSTEM = (
    "Anda penalar deret waktu yang teliti. Setiap klaim numerik HARUS berbentuk "
    "operasi dari pustaka yang diberikan, dihitung dari deret asli, sehingga bisa "
    "diverifikasi ulang. Jangan mengarang angka."
)

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


def _fmt_series(sample: Sample) -> str:
    vals = ", ".join(str(v) for v in sample.series.nilai)
    return f"[{vals}]"


def build_prompt(sample: Sample, mode: str = "panjang", max_steps: int | None = None) -> str:
    """User prompt for one item. Pure — no model call, safe to test offline."""
    instruksi = _MODE_INSTRUKSI.get(mode, _MODE_INSTRUKSI["panjang"])
    if max_steps is not None:
        instruksi += f" Pakai paling banyak {max_steps} langkah."
    return (
        f"Deret: {sample.series.nama} (satuan {sample.series.satuan}, {sample.series.freq}).\n"
        f"Konteks: {sample.konteks}\n"
        f"nilai = {_fmt_series(sample)}\n"
        f"Pertanyaan: {sample.pertanyaan}\n\n"
        f"{instruksi}\n{_FORMAT}"
    )


def _normalize_label(s: str) -> str:
    return s.strip().strip(".").lower()


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
        **llm_kwargs,
    ):
        self.model = model
        self.mode = mode
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._llm_kwargs = llm_kwargs
        self.name = name or f"qwen2.5-7b:{mode}" + (f":<= {max_steps}" if max_steps else "")
        self._llm = None
        self._SamplingParams = None

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

    def _generate(self, prompt: str) -> str:  # pragma: no cover - needs GPU
        llm = self._ensure_llm()
        sp = self._SamplingParams(temperature=self.temperature, max_tokens=self.max_tokens)
        convo = [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": prompt}]
        out = llm.chat(convo, sp)
        return out[0].outputs[0].text

    def predict(self, sample: Sample) -> tuple[list[ReasoningStep], str]:
        prompt = build_prompt(sample, mode=self.mode, max_steps=self.max_steps)
        text = self._generate(prompt)
        steps, label = parse_model_output(text)
        if self.max_steps is not None and len(steps) > self.max_steps:
            steps = steps[: self.max_steps]
            for i, s in enumerate(steps, start=1):
                s.langkah = i
        return steps, label
