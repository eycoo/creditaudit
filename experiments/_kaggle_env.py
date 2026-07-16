"""Env-driven vLLM overrides so the experiment `main()`s stay zero-arg.

The Kaggle notebook detects the GPU setup and exports these env vars *before*
launching the experiments, so the same code runs unchanged on:

- **2×T4** — `GEARTS_VLLM_TP=2` → tensor-parallel, full precision (clean baseline);
- **1×T4** — `GEARTS_VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct-AWQ` → 4-bit, fits 16 GB.

Unset vars fall through to `QwenVLLMAdapter` defaults, so nothing changes off-Kaggle.
"""
from __future__ import annotations

import os


def vllm_overrides() -> dict:
    """Build `QwenVLLMAdapter(**kwargs)` from environment; empty when unset."""
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
