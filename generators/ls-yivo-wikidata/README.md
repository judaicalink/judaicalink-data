# ls-yivo-wikidata: generator history

The YIVO Encyclopedia articles (dataset yivo) linked to their Wikidata items. New dataset of 2026-10-12 (decision
0025).

## Inputs

- `yivo/2020-09-30`: the articles, identified by the name in their `jl:describedAt` address.
- `inputs:web-caches/wikidata-yivo-2026-10-12/p8569.tsv`: every Wikidata item with a YIVO Encyclopedia ID (P8569),
  from the Wikidata Query Service on 2026-10-12 (the query is `p8569.rq` next to it).

## Generator

`generate.py`; the reading and matching is in `yivo_wikidata.py`, shared with record-classes. Names are compared
without case, accents, and with spaces, commas and hyphens as one separator. An article with exactly one item gets
`owl:sameAs` the item; with several items it is left out (5: ashkenaz, galicia, lewin_brothers, sephardim,
strashun_shemuel_and_matityahu).

Result 2026-10-12: 1,438 of 1,798 articles linked; 2 P8569 values name article subsections that yivo does not have
as articles (`Dance/Traditional_Dance`, `Language/Multilingualism`).
