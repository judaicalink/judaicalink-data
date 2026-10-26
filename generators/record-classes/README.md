# record-classes: generator history

The class of records that their datasets do not type. New dataset of 2026-10-12 (decision 0025); first part: the
1,798 articles of yivo, which have no `rdf:type`.

## Inputs

- `yivo/2020-09-30`: the articles and their abstracts.
- `inputs:web-caches/wikidata-yivo-2026-10-12`: `p8569.tsv` (the Wikidata items of the articles with their
  instance-of classes) and `classes-top.tsv` (for these 323 classes, which upper classes they belong to); the queries
  are next to them.

## Generator

`generate.py`, with `yivo_wikidata.py` of ls-yivo-wikidata. Rules, in this order:

1. the Wikidata class of the article's item: human `foaf:Person`; subclass of geographic location, administrative
   territorial entity or human settlement `schema:Place`; of organization `foaf:Organization` (also families that
   Wikidata types so); of written work, periodical or creative work `schema:CreativeWork`;
2. otherwise, life dates in parentheses at the start of the abstract (`(1880–1963), …`, `(ca. 1759–1837)`,
   `(Pseudonym of …; 1869–1942)`): `foaf:Person`;
3. otherwise `skos:Concept`.

Result 2026-10-12: 1,092 persons (986 by Wikidata, 106 by life dates), 199 places, 97 organisations, 54 works, 356
subjects. Known imperfections (for corrections): a few family articles whose item is one person. The 346 article
subsections (`skos:Concept` in yivo) are not typed here.

Version 2026-10-18: the classes of the common layer (`jl.classes`; 2026-10-12 wrote `jl:Place`, `jl:Work`,
`jl:Subject`); otherwise the same.

## Footprints persons (2026-10-25, decision 0034)

The Footprints API does not tell persons from organisations. `foaf:Organization` where the VIAF record named by
Footprints is an organisation (`viaf`) or the name names an institution, firm or group (`ORGANISATION` in
`generate.py`: libraries, universities, seminaries, congregations, booksellers, printing houses, heirs and partners,
"&", in English, German, Italian, French, Latin, Dutch, Hebrew and transliterated Hebrew); every other one
`foaf:Person`. A VIAF record that is a place or a work gives no class. Version 2026-10-26 (from footprints
2026-10-26): 885 organisations (41 by
VIAF, 78 by VIAF and name, 766 by name), 10,757 persons (1,267 by VIAF). Known imperfections: VIAF calls some
printers organisations (the firm that bears their name, e.g. "Proops", "Bragadin"); partnerships of two printers are
organisations by "&".
