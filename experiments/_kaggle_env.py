"""GPU-aware vLLM config so the experiment `main()`s stay zero-arg and zero-input.

The config is decided **in code** (not in a notebook cell) so it always travels
with the clone and can't go stale. `vllm_overrides()` auto-detects the GPUs and
picks a setup that fits Kaggle, unless `GEARTS_VLLM_*` env vars override it:

- **big single GPU** (≥20 GB: A6000/A100/L4/3090…) → full-precision Qwen2.5-7B, no
  quantization, no tensor-parallel (the cleanest, fastest baseline);
- **2×T4** → `tensor_parallel_size=2`, full precision split across the two cards;
- **1×T4** (small single GPU) → `Qwen/Qwen2.5-7B-Instruct-AWQ` 4-bit, which fits 16 GB.

`enforce_eager=True` skips torch.compile/cudagraph capture — on a memory-tight T4
that compile step itself OOMs, and for an 18-sample benchmark its throughput gain
isn't worth the minutes of compilation. `dtype=half` is forced only on pre-Ampere
cards (T4, compute < 8.0) that lack bfloat16; bigger cards keep bf16 (dtype auto).
Off-GPU everything falls back to `QwenVLLMAdapter` defaults, so the offline tests
are unaffected.
"""
from __future__ import annotations

import os

MODEL_AWQ = "Qwen/Qwen2.5-7B-Instruct-AWQ"
BIG_GPU_GB = 20  # ≥ this on one card → run the full 7B unquantized on it


def _gpu_count() -> int:
    try:
        import torch

        return torch.cuda.device_count()
    except Exception:  # torch absent / no CUDA → treat as no GPU
        return 0


def _min_gpu_mem_gb() -> float:
    """Smallest per-GPU total memory (GB), 0 if none/unknown."""
    try:
        import torch

        n = torch.cuda.device_count()
        return min(torch.cuda.get_device_properties(i).total_memory for i in range(n)) / 1e9
    except Exception:
        return 0.0


def _no_bf16() -> bool:
    """True on pre-Ampere GPUs (compute capability < 8.0) which lack bfloat16."""
    try:
        import torch

        major, _ = torch.cuda.get_device_capability(0)
        return major < 8
    except Exception:
        return False


def _auto_detect() -> dict:
    """A vLLM config sized to the visible GPUs (memory-aware)."""
    kw: dict = {
        "max_model_len": 4096,  # series prompts are short; small KV cache
        "gpu_memory_utilization": 0.92,
        "enforce_eager": True,  # skip torch.compile — avoids compile-time OOM, faster cold start
    }
    n = _gpu_count()
    if n == 0:
        return kw
    if _no_bf16():
        kw["dtype"] = "half"  # T4-class card: force fp16
    mem = _min_gpu_mem_gb()
    if n >= 2:
        kw["tensor_parallel_size"] = n  # split the 7B across GPUs, keep full precision
    elif mem < BIG_GPU_GB:
        kw["model"] = MODEL_AWQ  # small single GPU (≈16 GB T4) → 4-bit
    # else: big single GPU → full-precision Qwen2.5-7B, no AWQ, no TP
    return kw


def _env_overrides() -> dict:
    """Explicit operator overrides via environment (each wins over auto-detect)."""
    kw: dict = {}
    if os.environ.get("GEARTS_VLLM_MODEL"):
        kw["model"] = os.environ["GEARTS_VLLM_MODEL"]
    if os.environ.get("GEARTS_VLLM_QUANT"):
        kw["quantization"] = os.environ["GEARTS_VLLM_QUANT"]
    if os.environ.get("GEARTS_VLLM_TP"):
        kw["tensor_parallel_size"] = int(os.environ["GEARTS_VLLM_TP"])
    if os.environ.get("GEARTS_VLLM_GPU_UTIL"):
        kw["gpu_memory_utilization"] = float(os.environ["GEARTS_VLLM_GPU_UTIL"])
    if os.environ.get("GEARTS_VLLM_MAX_LEN"):
        kw["max_model_len"] = int(os.environ["GEARTS_VLLM_MAX_LEN"])
    if os.environ.get("GEARTS_VLLM_DTYPE"):
        kw["dtype"] = os.environ["GEARTS_VLLM_DTYPE"]
    return kw


def vllm_overrides() -> dict:
    """`QwenVLLMAdapter(**kwargs)`: auto-detect GPUs, then apply any env overrides."""
    kw = _auto_detect()
    kw.update(_env_overrides())  # explicit env vars win per key
    return kw
