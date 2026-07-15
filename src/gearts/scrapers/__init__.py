"""Source scrapers: real public series → raw `Series` JSONL (data/raw/).

Each scraper separates a thin network *fetch* layer from a pure *parse/
normalize* layer so normalization is testable offline. Scrapers emit bare
`Series` (no reasoning) — reasoning synthesis is a later phase (ADR-0002).
"""
