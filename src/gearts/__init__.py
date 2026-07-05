"""GEAR-TS — grounded, verifiable, token-efficient reasoning over time series.

The LLM emits reasoning as a sequence of operations over a numeric series;
the deterministic verifier (this package) recomputes each operation on the
original series and checks the claimed number. See project_brief.md.
"""
