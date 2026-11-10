# 0042 Place links stated by a source come before the ones we derived

Status: accepted · Date: 2026-11-10 · Amends [0022](0022-entity-pages-in-the-framework.md), [0038](0038-facts-per-class.md)

## Context

An entity page takes the text of a place from the record with the highest precedence and the place IRI from the
same record (0022, 0038). That record's IRI may have been derived from its text: geo-enriched looks the text up in a
gazetteer (in 2019: the first hit of the GeoNames search), records-normalized in dictionaries made from the links in
the data. Such a link then beat what Wikidata states, because Wikidata comes last in the precedence (0029). Moses
Hess (`ep/1025124`) was born in "Bonn"; geo-enriched 2019 had linked the text to Cologne Bonn Airport, and
records-normalized 2026-10-12, still made from geo-enriched 2019, carried that link to 97 records named "Bonn", his
GND record among them. Wikidata says Bonn.

## Decision

- **The place IRI of a page** (birth, death, burial, publication): a link stated by a source, Wikidata included,
  before a link derived from the text of a place (datasets geo-enriched and records-normalized); then, as before,
  the link of the record whose text the page shows; then the precedence.
- The text stays the text of the record with the highest precedence: the page shows what the source wrote, and links
  the place a source states for it.
- records-normalized keeps its links: they are statements about the records, made where a record has no link.

## Consequences

- Where only a derived link exists, the page keeps it; wrong derived links are fixed in their datasets.
  records-normalized reads the stable versions of its inputs since 2026-11-10 (it had pinned them and still read
  geo-enriched 2019 after geo-enriched 2026-10-16 had replaced the first-hit links).
- Where the sources name different places, the page may show the text of one record with the link of another (the
  text "France", the link Uman of Wikidata). Such conflicts are to be stated in a dataset of their own.
