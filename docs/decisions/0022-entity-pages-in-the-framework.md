# 0022 Entity pages in the framework: versions of `ep`, a fresh closure each run, merges and splits by comparison

Status: accepted (points 1–4; ontology terms and the remaining rules still open) · Date: 2026-10-12 · Amends
[0009](0009-entity-pages.md), supersedes [0010](0010-nli-exception.md)

## Context

0009 made every entity-page set a dataset of its own (`ep-<date>`); the generator framework (0018) has versions.
`ep-2026-10-06` (made by `kg-complements/ep_generator.py`, never published) kept the previous clusters together and
added links on top, so groups could only grow: an error in the legacy clusters could never be corrected, and the
only split was a special case (group records). Its guards against joining different Wikidata items refused links in
the order they came. The goal: mistakes can be fixed, and entity-page IRIs stay stable.

## Decision

### 1. Sets are versions of `ep`

- A new set is a new version of the dataset `ep` (after the legacy version 2021-05-28), not a dataset `ep-<date>`.
  `stable` is the current set; the graph `datasets/ep` holds it, so only one set is ever loaded; no
  `dcterms:replaces` between sets. The previous set is an input of the generator (`ep/<stable version>`).
- Event dates (`jl:mergeDate`, …) are the date of the run: data, not version ids (0018).

### 2. `ep-2026-10-06` is not carried over

It is not imported and becomes no version. The first framework version is made from `ep` 2021-05-28, the published
state `ep-2026-10-06` was made from. Its new numbers (2,717,191–2,937,178) were never published (checked
2026-10-12: nothing in the site, the catalogue, the demonstrators, the dashboard or the queries uses them), so they
may be assigned again. Its output is only a check for the port; then it moves to `lokal/work/`.

### 3. Files

- `ep.ttl.gz`: the entity pages; `ep-history.ttl.gz`: one statement per event for IRIs that are no longer pages.
  Both are in the graph `datasets/ep`.
- The history of a new version contains every triple of the previous history (history is never rewritten); every
  IRI of the previous version is a page or in the history of the new one. The generator checks both. So the highest
  number ever used is the highest number in the previous version: no `jl:highestEntityPageNumber`.
- The run report is not published: counts in the run record, lists (conflicts, splits) in the log.

### 4. The algorithm

- **Groups** are computed fresh in every run: the transitive closure of the identity links over the records
  (JudaicaLink resources of the core classes). Entity pages are never part of the closure; the previous set is read
  only for the comparison.
- **Comparison** of each new group with the old groups (the records of the previous pages):

  | New group | Result |
  |---|---|
  | contains exactly one old group (possibly plus new records) | the IRI is kept |
  | contains several whole old groups | the oldest IRI (lowest number) is kept; the others get `jl:mergedInto` + `jl:mergeDate` |
  | the records of an old group lie in two or more new groups | the old IRI gets `jl:splitInto` (all parts) + `jl:splitDate`; always a split, also when a part lands in an existing page; no part keeps the old IRI |
  | contains no old group | a new IRI above the highest number ever used |
  | an old group with no record left | `jl:retiredDate` |

- A merged IRI keeps its meaning (the same entity), so it can be redirected; `jl:mergedInto` instead of
  `dcterms:isReplacedBy`. A split IRI changes its meaning ("stood for several entities, which we did not know"), so it
  cannot be redirected; `jl:splitInto` is not a sub-property of `dcterms:isReplacedBy`.
- **Deprecated record IRIs** are nodes of the closure, never members of a page: a record IRI replaced by exactly one
  other (e.g. `data/Aachen dcterms:isReplacedBy data/geonames/Aachen`: `ep/1` stays `ep/1` and represents only the
  new IRI), and the IRIs of a superseded dataset (e.g. the legacy NLI URIs, linked to their records by
  `ls-nli-legacy`). A replacement by several IRIs is a split: in the comparison the old member stands for all of
  them; it is not part of the closure.
- **Identity links:** `owl:sameAs`, `gndo:gndIdentifier` (IRI or literal) and replacements by one IRI. Every target is
  a key after normalisation (GND `…/gnd/N`, `…/N/about`, `https`, `data/gnd/N`; VIAF incl.
  `https://viaf.org/viaf/http://viaf.org/viaf/N/`; LC `authorities/names/nN` = `authorities/nN`; GeoNames `sws.`,
  `www.`, trailing slash, `data/geonames/N`; DBpedia `dbpedia.org/resource/X` = `data/dbpedia/X`, language editions and
  Wikipedia articles per language). **The same key joins; different keys never prevent a join**: no guards, so the
  result depends only on the links, not on their order.
- Links to something that is not one entity (a web page, a disambiguation page, a broader concept) and wrong links
  are mistakes in the data: they are removed by correction datasets ([0023](0023-correction-datasets.md)), not by
  rules of the generator. The run report lists what points to them: groups with several Wikidata items, records of
  incompatible classes (person, place, work) in one group, keys shared by many records of one dataset.

### 5. The legacy NLI pages (supersedes 0010)

They are handled by the comparison like all others: through the `owl:sameAs` of `ls-nli-legacy` the legacy page of
a URI that stands for one person record keeps its IRI and represents that record (179,796 URIs); pages of URIs made
from several people are split (1,474), the others retired. Every published IRI keeps a record of what happened to
it; no exception is needed.

## Measured (2026-10-12, stable versions; `lokal/work/ep-measure/`)

- The legacy set has 1,717,191 pages: 749,446 TagMe mentions, 362,258 Compact Memory pages, 316,166 page images
  (UB Frankfurt), 182,445 legacy NLI persons, 48,191 groups of several members, the rest records without links and
  web pages that were only link targets. Only records of the core classes get pages: about 295,000.
- The 2021 generator used only `owl:sameAs` (all graphs of the endpoint then, with one blacklisted IRI). Today's
  data still holds every legacy group together: a fresh `owl:sameAs` closure splits none of the 48,191.
- Pure closure over all identity links and keys (without the two non-identifiers below): 295,198 groups, the largest
  with 9 records; of the 78,250 legacy pages with a record none is split, 4,706 are merged into another. 57 groups
  hold several Wikidata items (mostly Wikidata duplicates of one person; about 8 real conflations, already in the
  legacy pages, e.g. Randolph Churchill father and son, Hai Gaon and Sherira Gaon), 20 records of incompatible
  classes (typing errors in footprints and rujen, NLI work records).
- Non-identifiers found: bhr states `owl:sameAs` the DNB EntityFacts service page for 783 records (a group of
  1,815 records if used; it was the 2021 blacklist); one Russian Wikipedia disambiguation page (Granada, Grenada).

## Consequences

- `ep_generator.py` is ported with this algorithm (closure, comparison, history files and checks); the rules for
  facts (precedence, languages, labels) are kept, with `jl:occupationURI` (0020) and the dataset names of the
  catalogue.
- The ontology pull request for entity pages (0020) gets `jl:mergedInto`; `jl:splitInto` without
  `dcterms:isReplacedBy`.
- The two non-identifiers become the first correction dataset (0023), before the first `ep` version.
- Still to decide: the ontology pull request, and the rules of 2026-10-06 to revisit (precedence list with the
  catalogue's dataset names, organisations outside the core).
