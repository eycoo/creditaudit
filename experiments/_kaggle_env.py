"""GPU-aware vLLM config so the experiment `main()`s stay zero-arg and zero-input.

The config is decided **in code** (not in a notebook cell) so it always travels
with the clone and can't go stale. `vllm_overrides()` auto-detects the GPUs and
picks a setup that fits Kaggle, unless `GEARTS_VLLM_*` env vars override it:

- **2×T4** → `tensor_parallel_size=2`, full precision (cleanest baseline);
- **1×T4** → `Qwen/Qwen2.5-7B-Instruct-AWQ` 4-bit, which fits one 16 GB card.

`enforce_eager=True` skips torch.compile/cudagraph capture — on a memory-tight T4
that compile step itself OOMs, and for an 18-sample benchmark its throughput gain
isn't worth the minutes of compilation. Off Kaggle (no torch/GPU) everything falls
back to `QwenVLLMAdapter` defaults, so nothing changes for the offline tests.
"""
from __future__ import annotations

import os

MODEL_AWQ = "Qwen/Qwen2.5-7B-Instruct-AWQ"


def _gpu_count() -> int:
    try:
        import torch

        return torch.cuda.device_count()
    except Exception:  # torch absent / no CUDA → treat as no GPU
        return 0


def _auto_detect() -> dict:
    """A vLLM config sized to the visible GPUs (Kaggle T4 / T4×2)."""
    kw: dict = {
        "dtype": "half",  # T4 (compute 7.5) has no bfloat16
        "max_model_len": 4096,  # series prompts are short; small KV cache
        "gpu_memory_utilization": 0.92,
        "enforce_eager": True,  # skip torch.compile — avoids the compile-time OOM
    }
    n = _gpu_count()
    if n >= 2:
        kw["tensor_parallel_size"] = n  # split the 7B across GPUs, keep full precision
    elif n == 1:
        kw["model"] = MODEL_AWQ  # 4-bit fits a single 16 GB T4
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
