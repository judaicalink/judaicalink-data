# ls-rujen-wikidata: generator

The articles of the Encyclopedia of Russian Jewry (rujen) linked to their Wikidata items.

## Inputs

- `rujen/2020-09-28/rujen.jsonl.gz`: the crawl, for the page ids and names; the record IRIs are made with rujen's
  `local()` (shared code, `load_shared("rujen", "generate")`), the main page left out as rujen does.
- `inputs:web-caches/wikidata-rujen-2026-10-15/p10278.tsv`: every Wikidata item with an Encyclopedia of Russian Jewry
  ID (P10278), from the Wikidata Query Service on 2026-10-15 (the query is `p10278.rq` next to it). The value is
  mostly the page id (`index.php?curid=<id>`), once the page name (`РАЙЦИН_Эфраим`).

## Framework generator

`generate.py` (2026-10-15): every record with exactly one item gets `owl:sameAs` that item; records with several
items, items with several records and values naming no page are left out and logged. First run: 28 values, 28
links, nothing left out. Deterministic, no network access.
