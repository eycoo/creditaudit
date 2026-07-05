# Inventaris sumber deret publik

Status: ready-for-agent
Difficulty: easy

## Spec

Produce a markdown inventory of candidate public time-series sources (brief §9.1). For each source: name,
URL/endpoint, domain (health / food price / weather / energy), access method (official API vs scrape),
frequency + typical length available, and a license/ToS note (public data only, brief §17.1).

Cover at least: PIHPS/Bank Indonesia (food prices), Kemenkes dashboards (disease/DBD cases), BMKG (weather),
plus open energy-load sources.

Write the inventory to `.scratch/fase-1-fondasi/sumber-deret.md`. No scraping — inventory only.

## Acceptance

- ≥10 candidate sources listed with the fields above.
- Zero actual data collection performed.

## Comments
