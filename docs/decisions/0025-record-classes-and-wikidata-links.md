# 0025 Classes of untyped records (record-classes) and Wikidata links of YIVO (ls-yivo-wikidata)

Status: accepted · Date: 2026-10-12

## Context

Entity pages are made from records of the core classes (0022). The 1,798 articles of yivo have no `rdf:type`, so they
were on no entity page (only the 346 article subsections, typed `skos:Concept`, were taken as subjects). Their class
can be read from the text (life dates at the start of the abstract) only for persons; places, organisations, works and
topics are not told apart reliably that way. Wikidata names the YIVO article of 1,453 items (P8569) and gives their
classes; these items are also identity links to the other records of the same entity.

## Decision

- **`record-classes`** (kind complement, methods lookup and rule-based, automated): the place for the classes of
  records that their datasets do not type. A new version of the record dataset is not used: the classes are assigned
  automatically, which would make the record dataset automated (0018, 0020). First part: the yivo articles, by the
  class of their Wikidata item (human, place, organisation, work), else by life dates (person), else `jl:Subject`.
  Later parts (the untyped GeoNames nodes, haskala/djh records) go into the same dataset.
- **`ls-yivo-wikidata`** (kind linkset, method lookup): yivo article `owl:sameAs` its Wikidata item, where there is
  exactly one.
- Both read one snapshot of the Wikidata Query Service (`inputs:web-caches/wikidata-yivo-2026-10-12`, the queries
  next to the answers); generators do not query services themselves (0021). The matching code is shared
  (`generators/ls-yivo-wikidata/yivo_wikidata.py`).
- The article subsections are not typed (open).

## Consequences

- `ep` reads both: the classes of record-classes count for the records they are about, and `jl:Subject` is a class
  of entity pages; the Wikidata links join YIVO articles with other records.
- Wrong classes or links of single articles (family articles whose Wikidata item is one person) are fixed by
  correction datasets (0023, 0024).
