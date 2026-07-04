# CONTEXT.md — Domain Glossary

Ubiquitous language for this project. Use these exact terms in issues, tests, ADRs, and code. Indonesian terms are canonical (they key into the dataset schema and the brief); English descriptions for clarity.

## Products & actors

| Term | Meaning |
|---|---|
| **pinjol** | Online lending (pinjaman online); colloquially often implies the illegal kind |
| **Pindar** | Pinjaman daring — OJK's rebrand for *legal* online lending (POJK 40/2024) |
| **paylater** | Buy Now Pay Later consumer credit (POJK 32/2025) |
| **OJK** | Otoritas Jasa Keuangan — financial services regulator, source of compliance rules |
| **Satgas PASTI** | Task force for illegal financial activity |
| **penawaran** | A credit offer (ad, app screen, installment table) — the system's input unit |

## Financial terms (schema fields — names are law, see `src/creditaudit/schema.py`)

| Term | Meaning |
|---|---|
| **pokok** | Principal amount |
| **bunga_nominal / bunga_basis** | Stated interest rate and its basis: `harian` (daily), `bulanan`, `tahunan`, `flat` |
| **tenor_hari** | Loan term in days |
| **biaya_admin** | Admin fee, basis `persen` or `nominal` |
| **potongan_di_depan** | Upfront deduction from disbursed amount |
| **denda / denda_basis** | Late penalty and its calculation base: `sisa_pokok` (remaining principal — correct), `limit_awal` (initial limit — a common misleading base), `harian` |
| **dana_bersih_diterima** | Net funds actually received (pokok − upfront cuts) |
| **total_bayar** | Total repayment |
| **biaya_efektif** | True effective cost (rupiah and % per month) — the number the system exists to reveal |
| **lock cap** | OJK ceiling: total repayment burden (bunga + denda) ≤ 100% of pokok |
| **fine print** | Small/hidden text where real terms hide (`teks_fine_print` in schema) |

## Misleading-fee taxonomy (multi-label; P = cost misleading, R = legality red flag)

| Code | Name |
|---|---|
| P1 | Misrepresentasi suku bunga — interest framed small/without context |
| P2 | Biaya siluman — hidden fees, upfront cuts not in headline |
| P3 | Salah basis perhitungan denda — penalty computed from wrong base |
| P4 | Penyamaran struktur cicilan — "light installments" hiding long tenor |
| P5 | Framing visual menyesatkan — visual emphasis tricks (realized at image render) |
| P6 | Klaim palsu atau bait — false "0% / no fee" claims |
| R1 | Indikator ilegalitas — rate above OJK cap, excessive access requests, unsolicited channel offers |

## Architecture (see `docs/adr/`)

| Term | Meaning |
|---|---|
| **M1 Perception** | VLM (Qwen2.5-VL-7B) — offer image → structured JSON terms |
| **M2 Quantitative Reasoning** | Reasoning model + **deterministic calculator** — terms → true cost |
| **M3 Classification & Compliance** | Learned misleading-label classifier + untrained OJK **rule engine** |
| **M4 Explanation** | Plain-Indonesian summary, grounded to calculator numbers |
| **PoT (program-of-thought)** | Model emits a calculation *plan*; the Python calculator executes it. The model never does arithmetic for audited figures (ADR-0002) |
| **CoT-injection** | Dataset method: correct distilled reasoning + systematic misleading-presentation transforms → automatically labeled samples |

## Terms to avoid

- Don't say "fraud/scam detection" — the task is **penyesatan biaya** (cost misleading) detection; legality is only R1.
- Don't call M2's output "estimate" — calculator output is **deterministic**, call it computed true cost.
- Don't use "interest" ambiguously — always pair rate with its **basis** (harian/bulanan/tahunan/flat).
