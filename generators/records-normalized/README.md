# records-normalized: generator

Normalised dates, places and occupations of the records (new dataset, decision 0020: dates-normalized, places-linked,
occupation-concepts and occupation-fix of kg-complements combined).

## History

- 2026-10-06 (Kai Eckert): the four builders in kg-complements (`datasets_algorithmic.py`, `datasets_deterministic.py`),
  querying all graphs of the local endpoint; outputs in `dumps-additions/`, never published.

## Framework generator

`generate.py` (2026-10-12): a port of the four builders without changes to their logic. "All graphs" are the 18
versions that hold what they read (checked 2026-10-12 against all stable versions and the kg-complements outputs):
the record datasets bhr, dbpedia-persons, djh, epidat, footprints, geo-enriched, gnd-persons,
gnd-persons-entityfacts, haskala, hhkeydocs, hirsch-family, jre, nli-records, sosy, ubffm-persons, and for the place
dictionaries rujen, geo-coordinates and cm-entities. About 15 seconds.

Checked against the kg-complements outputs with `--param legacy_terms=true --input footprints=footprints/2025-03-21
--input haskala=haskala/2025-03-24` (the versions the endpoint held on 2026-10-06): occupations (6,815) and the typo
fix (2,900) identical; dates and places contain all old triples plus 55 dates and 36 places of haskala records, whose
graph the endpoint of 2026-10-06 did not hold.

Differences of the dataset (decided 2026-10-12):
- the stable versions footprints 2024-03-18 and haskala 2019-07-01 are complemented: 1,839 and 274 more dates, 116 more
  places (haskala); 184,388 date and 49,754 place triples;
- `jl:occupationURI` instead of `jl:occupationConcept`, and every occupation IRI stated with `jl:occupation` or
  `jl:occpation` (15,340, against the literal range of `jl:occupation`) is stated as `jl:occupationURI`; the typo fix
  is part of that, so there is no separate file: 22,155 occupation triples.
