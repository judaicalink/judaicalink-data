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
  places, classes and identifiers as the source gives them: `gnd` (replacing gnd-persons and gnd-persons-entityfacts),
  `lc`, `geonames`, `viaf`, `wikidata`, `dbpedia` (replacing dbpedia-persons, 0031). Each is made from a dump or query answer in the
  inputs area; its file name, checksum and version are in the run record and the `-meta` of every version made from
  it; a newer dump is a new input and gives a new version.
- **`jl:sameAs` for the identity JudaicaLink states** (decided 2026-10-16): a subproperty of `owl:sameAs`, used by
  the linksets and by the entities of `ep` for their records (instead of `jl:represents`); `owl:sameAs` in a record
  dataset is a statement of its source. The entity-page closure follows `jl:sameAs` (and, until they are made again,
  the `owl:sameAs` of the older linksets), the replacements of our own IRIs and the authority namespaces. An entity in
  `ep` has the class of what it is (`foaf:Person` …); `jl:EntityPage` is deprecated (its role is given by the dataset,
  the web page about an entity is its description, as VIAF separates a cluster from its page). Labels of foreign terms
  likewise: `jl:label` (subproperty of `rdfs:label`), in the ontology, which describes the common layer.
- **One linkset per authority dataset** (`ls-gnd`, `ls-viaf`, `ls-lc`, `ls-geonames`, `ls-wikidata`, `ls-dbpedia`; decided
  2026-10-16): it finds every reference to its authority in all our datasets (`jl.identifiers`), resolves it through
  the authority dataset to the current record (replacements), and links each referencing record to that record, by
  stated rules: a match must be unique; ambiguous cases are left out and logged. The links form a star (record →
  authority record), not pairs of datasets; a new dataset needs no new linkset. `ls-wikidata` also links the records
  whose source identifiers Wikidata states (BHR, YIVO, rujen); the Wikipedia articles are linked by `ls-dbpedia`
  (0031). Only the identity a dataset declares counts, and only for units above the quality threshold (0032). The pairwise linksets ls-nli-wikidata, ls-bhr-wikidata and ls-rujen-wikidata (never published) are
  dropped; ls-yivo-wikidata is replaced by ls-wikidata. The few direct links between our records (e.g. bhr → djh)
  get one linkset of their own.
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
- **The authority datasets select from each other** (decided 2026-10-18; worklist 2026-10-19): an authority dataset
  holds the records that our record datasets or the other authority datasets link to. If we trust Wikidata, the GND
  numbers it states for our entities are ours to take as well. The selection lists the linking dataset of every
  identifier, so the records that only an authority brings in can be told apart. Of an authority dataset only the
  declared identity statements select ([0032](0032-identity-declarations.md)), not its places of birth, occupations
  or related persons: through these the cascade would take in the neighbours of our entities (the first try reached
  Essen and Nordrhein-Westfalen through a place of birth). The selection is one worklist (`jl cascade`,
  `src/jl/cascade.py`), not rounds of generator runs: it starts from the seeds (every identifier our record datasets
  name, our linksets that are not made from the authority datasets, and the static lists of each authority dataset),
  resolves each new identifier to the current one, follows the declared identity links of the current records, and
  ends when nothing is pending; selections only grow within a cascade. Its output is an input
  (`inputs:cascade/<date>`), from which each authority generator runs once; then all runs and the linksets become
  versions together (`jl add-version` with several runs).
- **One entity, all identifiers, one value per fact** (decided 2026-10-18): connecting identifiers is the purpose
  of JudaicaLink, so an entity links every identifier its records and our linksets give it, also several of one
  authority (the GND's historic names of a place, its duplicates, the LC's duplicates, a city and its municipality in
  GeoNames): what our sources state as the same is not our mistake. A replaced identifier is linked as its
  successor. Facts are not doubled: each (name per language, life dates, places, coordinates, abstract per language)
  comes from the first record by a fixed order: dataset precedence; then within one dataset, the record that no
  other record of the group succeeds (Vilnius before Wilna), not a pseudonym of one (`gndo:realIdentity`), a
  populated place before an administrative unit (GeoNames class P before A; PPLC, PPLA, …, PPL), the record more of
  our datasets name, the lowest identifier. The run log lists the entities with several identifiers of one authority
  and the authority datasets are checked against each other (`jl check-authority-links`).
- **VIAF gets the benefit of the doubt:** a VIAF match is linked unless the data of the two sides contradict each
  other (birth or death dates given on both sides that differ); the contradictions are left out and logged.
- **Transition:** the linksets are made for all joins that the sources' links make today, so that the entity pages
  stay the same. The next ep version with `identity = linksets` is made when the identity report shows no join
  missing except those left out on purpose (named, with the rule that left them out).

## Consequences

- To do, in this order: the record datasets made again (bhr from a full harvest of the portal, epidat, hhkeydocs,
  rujen, …); the authority datasets (`gnd`, `lc`, `geonames`, `wikidata`, `viaf`; kind `authority`); the linksets
  per authority dataset; then ep with `identity = linksets`, compared with the previous version.
- The existing linksets made from sources' links of earlier years (2014links, interlinks, dbp-wiki-geo-linking,
  ls-nli-legacy) count as ours; they are made again where their sources allow.
- The licences of the source datasets follow their sources (VIAF: ODC Attribution 1.0, with canonical
  `https://viaf.org/viaf/<n>` URIs; GeoNames: CC BY 4.0; LC: public domain; Wikidata, GND: CC0).
