# Calculator: implement denda computation (basis sisa_pokok vs limit_awal)

Status: ready-for-agent
Difficulty: medium

## Spec

`src/creditaudit/calculator.py` computes bunga but not denda. Add:

- `hitung_denda(term: TermFinansial, hari_terlambat: int, sisa_pokok: float) -> float`
  - `denda_basis == "sisa_pokok"`: denda = `denda`% × sisa_pokok × hari_terlambat (the correct base per OJK)
  - `denda_basis == "limit_awal"`: denda = `denda`% × pokok × hari_terlambat (the *misleading* base — needed to compute what a misleading offer implies, P3 in `CONTEXT.md`)
  - `denda_basis == "harian"`: flat `denda` rupiah × hari_terlambat
  - `denda_basis` None/other → raise ValueError (fail loud, ADR-0002 discipline)
- Extend `cek_kepatuhan` in `rules.py`: lock cap must use `total_bunga + total_denda` vs 100% pokok (remove the `# ponytail:` bunga-only shortcut; take denda as an optional arg defaulting to 0).
- Tests: one case per basis; a P3 case showing sisa_pokok vs limit_awal give different denda for the same offer; lock-cap breach via denda alone.

## Constraints

- All arithmetic stays in `calculator.py` (ADR-0002).
- Schema field names unchanged.

## Acceptance

`pytest` green; lock-cap test with denda passes; `# ponytail` comment in `rules.py` removed.

## Comments
