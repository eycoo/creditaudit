"""Model adapters for the experiment harness.

Each adapter satisfies `gearts.harness.ModelAdapter` (a `.name` and a
`predict(sample) -> (reasoning_steps, answer_label)`). Heavy runtimes (vLLM,
CUDA) are imported **lazily inside `predict`**, so these modules import — and the
prompt/parse helpers test — offline, with no GPU.
"""
