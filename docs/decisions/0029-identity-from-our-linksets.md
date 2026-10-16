# 0029 Identity on the entity pages only from our linksets; external sources on file, trusted and described

Status: proposed · Date: 2026-10-16 · Amends [0022](0022-entity-pages-in-the-framework.md)

## Context

The entity pages (0022) join records by the transitive closure of every identity link in every dataset: the
`owl:sameAs` and GND numbers the sources state (a VIAF number in an NLI record, a GND number in bhr, the identifiers
EntityFacts lists) join pages as much as the links we made ourselves. The evidence for such a join (the VIAF cluster,
the Wikidata item and its statements) is not on file, and a wrong link in a source joins pages without any decision
of ours. Linksets we made (ls-yivo-wikidata, ls-nli-wikidata) apply rules (unique matches only) that the sources'
links bypass.

The identity report of the ep generator (run of 2026-10-16 on the stable versions) measured the dependency: of 310,214
groups, 14,343 (36,713 records) would be split if only the linksets counted. Adding linksets by key, one after the
other, leaves split: GND 9,469 groups; + VIAF 880; + LC 786; + Wikidata 71; + DBpedia 36; + GeoNames 3; + the direct
links between JudaicaLink records 0. ISNI, Wikipedia articles and other web addresses (BnF, BMLO, ORCID) join nothing
the others do not.

## Decision

- **Identity on the entity pages comes only from our own statements:** the linksets (catalogue kind `linkset`), the
  replacements our generators state (`dcterms:isReplacedBy`), and records in an authority namespace
  (`data/gnd/<n>` is GND n). The identity statements of the record datasets stay in them as facts of their sources,
  but the closure does not follow them. The ep generator has the parameter `identity` (`all`: 0022; `linksets`: this
  decision) and always reports the joins that only links outside the linksets make, by dataset and key.
- **External sources are kept on file as datasets** with the parts we use: every entity that a record or a linkset
  of ours reaches (also the ones a linkset leaves out, as the evidence for leaving them out), with labels, dates,
  places, classes and identifiers as the source gives them: `wikidata`, `viaf`, `lc`, `geonames` (new), the GND
  (gnd-persons, gnd-persons-entityfacts) and DBpedia (dbpedia-persons). Each is made from a dump or query answer in the
  inputs area; its file name, checksum and version are in the run record and the `-meta` of every version made from
  it; a newer dump is a new input and gives a new version.
- **Linksets are made by key** (GND, VIAF, LC, Wikidata, DBpedia, GeoNames, direct links between our records) from
  the identifiers in our records and in the source datasets, by stated rules: a match must be unique in both
  directions; ambiguous cases are left out and logged.
- **We trust the sources and point to them.** Identifier statements of authority files and knowledge bases are taken
  as given; we do not repair them. When a link is wrong, its provenance (record, identifier, source dataset, dump)
  leads to the source, where it is reported. Every source dataset describes the character of its data (who makes it
  and how, e.g. GND records made by cataloguers, VIAF clusters formed by an algorithm from the records of many
  libraries, Wikidata edited openly and partly by bots), and every linkset names the identifiers and sources it relies
  on and points to those descriptions.
- **Deprecated and deleted identifiers are data of the source datasets,** never `owl:sameAs`, whatever the source
  says: an identifier the source has replaced is stated with the source's own IRIs,
  `<old> dcterms:isReplacedBy <current>` (e.g. `https://d-nb.info/gnd/5210156-3` by `https://d-nb.info/gnd/4028586-8`);
  an identifier the source has deleted without a successor as `<old> owl:deprecated true`. Where we already have an
  entity of our own for the old identifier (`data/gnd/<old>`), it is stated `dcterms:isReplacedBy` our entity for
  the current one, as for any of our IRIs; otherwise no IRI is coined for the old identifier. Only replacements
  between our own IRIs are identity for the closure; the replacements of external identifiers are evidence for the
  linksets, which look up through `owl:sameAs` and `dcterms:isReplacedBy`.
- **Links to JudaicaLink are never evidence.** A statement of an external source that points to JudaicaLink (an IRI
  in `data.judaicalink.org`, a property such as Wikidata's P13183 "JudaicaLink person (GND) ID") most likely comes
  from our own data (our BEACON in EntityFacts, entity pages copied into Wikidata) and would confirm our own mistakes.
  Such statements are left out when a source dataset is made. Where the source records references (Wikidata),
  identifier statements whose reference cites JudaicaLink are left out as well.
- **Canonical forms:** external IRIs are written in the form their source uses ([iri-forms.md](../iri-forms.md),
  `src/jl/iris.py`); every run reports the IRIs it writes in another form. A canonical form changes only the
  spelling, never the identifier. Coordinates likewise: `"POINT(<lon> <lat>)"^^geosparql:wktLiteral`, the numbers
  as the source gives them (decided 2026-10-16).
- **VIAF gets the benefit of the doubt:** a VIAF match is linked unless the data of the two sides contradict each
  other (birth or death dates given on both sides that differ); the contradictions are left out and logged.
- **Transition:** the linksets are made for all joins that the sources' links make today, so that the entity pages
  stay the same. The next ep version with `identity = linksets` is made when the identity report shows no join
  missing except those left out on purpose (named, with the rule that left them out).

## Consequences

- To do, in this order: the source datasets (`wikidata`, `viaf`, `lc`, `geonames`; GND and DBpedia exist), then the
  linksets by key; then ep with `identity = linksets`, compared with the previous version.
- The existing linksets made from sources' links of earlier years (2014links, interlinks, dbp-wiki-geo-linking,
  ls-nli-legacy) count as ours; they are made again where their sources allow.
- The licences of the source datasets follow their sources (VIAF: ODC Attribution 1.0, with canonical
  `https://viaf.org/viaf/<n>` URIs; GeoNames: CC BY 4.0; LC: public domain; Wikidata, GND: CC0).
