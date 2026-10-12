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
   territorial entity or human settlement `jl:Place`; of organization `foaf:Organization` (also families that
   Wikidata types so); of written work, periodical or creative work `jl:Work`;
2. otherwise, life dates in parentheses at the start of the abstract (`(1880–1963), …`, `(ca. 1759–1837)`,
   `(Pseudonym of …; 1869–1942)`): `foaf:Person`;
3. otherwise `jl:Subject`.

Result 2026-10-12: 1,092 persons (986 by Wikidata, 106 by life dates), 199 places, 97 organisations, 54 works, 356
subjects. Known imperfections (for corrections): a few family articles whose item is one person. The 346 article
subsections (`skos:Concept` in yivo) are not typed here.
