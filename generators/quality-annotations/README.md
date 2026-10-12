# quality-annotations: generator

Quality annotations (DQV, Web Annotation) for problems in the data that cannot be fixed by adding facts (new dataset,
decision 0020).

## History

- 2026-10-06 (Kai Eckert): `quality_annotations` in kg-complements (`datasets_algorithmic.py`), 4,636 annotations
  from the local endpoint and hand-written notes; output in `dumps-additions/`, never published.

## Framework generator

`generate.py` (2026-10-12): the checks run on the stable versions of the record datasets (the inputs of
`records-normalized`, whose date rules it uses as shared code), `compact-memory` 2026-10-12, `geo-coordinates` and
`nrwbibdjg`. About 40 seconds.

What was kept, changed and dropped (decided 2026-10-12):
- **Kept, from the data:** the dates `records-normalized` cannot normalise (2,692 in 2026-10-06), with the reason
  (`why_not` of records-normalized). The first run found 2,953; with the rules added to records-normalized for them
  (2026-10-12, before either was published) 585 are left, plus 51 records whose death date is before their birth
  date (Aeschylus 0525–0456 in ubffm-persons), whose dates records-normalized now leaves out; the problems of single
  versions, now found by checks instead of written by hand and targeted at the version (`datasets/<slug>/<version>`), not the dataset: RDF-star in epidat, `jl:occpation` in bhr,
  `dcterms:created` as plain strings in nrwbibdjg, `jl:lat`/`jl:lon` swapped in geo-coordinates (all 3 places that
  have them; the others have only `geo:asWKT`, which is right), and IRIs as values of `jl:occupation` in
  dbpedia-persons, gnd-persons and sosy (one note on the property before; sosy's are addresses of HTML views).
- **Changed:** the isolated years of Compact Memory are checked on the issues of `compact-memory` with the rule of
  the full-text bundle's `date_review.tsv` and annotated on the issue, which states the date (0008), not on its 513
  pages: 16 issues, the 14 of the review list and 2 with the years 1 and 965, which the bundle did not list. The
  garbled article title (page 3331118) is annotated on the article. IRIs `data/quality-annotations/annotation/<hash>`
  instead of `datasets/quality-annotations/a/<hash>`; no `dcterms:created` (it was the time of the run, so no two
  runs were alike; the version says when).
- **Dropped:** the 1,403 broken `owl:sameAs` of the legacy entity pages (complements are never about entity pages,
  0008; a matter for the next entity-page set) and the 18 notes on the state of the old catalogues and dumps:
  self-descriptions and script links (gone with 0018), the dump of `occupations`, catalogue dates (hhkeydocs fixed;
  gba's is the date of its first version), the licence name "CC4.0" (fixed in the catalogue, 2026-10-12), djh's
  licence "unknown" (true), and the tar archives named `.ttl.gz` (none left in the store, 0015).
