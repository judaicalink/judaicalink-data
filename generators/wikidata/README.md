# wikidata: generator

The Wikidata items JudaicaLink uses (decision 0029), from answers of Wikidata kept in the inputs area.

## History

- 2026-10-16 (Kai Eckert): new dataset.

## Inputs

- `inputs:web-caches/wikidata-2026-10-16`, made by `query.py`:
  - `find-<P>.rq` / `.tsv`: the Wikidata Query Service, which items state an identifier our data names (P227 GND,
    P214 VIAF, P244 LC, P1566 GeoNames, P213 ISNI); the answers as the service gives them, in batches of 3,000
    values.
  - `articles.tsv`: the Wikidata API (`wbgetentities`, `sites=enwiki`, `titles`), the items of the English Wikipedia
    articles of the DBpedia resources our data names (title as in the DBpedia IRI, underscores as spaces; titles
    that are redirects in Wikipedia find no item).
  - `entities.jsonl.gz`: the Wikidata API (`wbgetentities`, 50 items per request), the content of all items found,
    one line per requested item, reduced to the labels (en, de, he, mul), the sitelinks (enwiki, dewiki, hewiki) and
    the statements of P31, P19, P20, P569, P570, P227, P214, P244, P1566, P213, P8189, P8569, P10405, P10278 (rank,
    value, and of the references only P248, P143, P854). A merged item is answered under its old id with
    `"redirect"`, a deleted one without `"entity"`.
- The identifiers our data names: our datasets and the other authority datasets (`jl.authorities.linking_inputs`:
  the stable versions, or the runs given with `--use` to `query.py` and `jl generate`), and the runs of linksets that
  are no versions yet (`ids.py`: `RUNS`).

The Query Service was used only for the lookups by identifier: on 2026-10-16 it throttled and timed out on the
content queries, and the API answers 50 items with all their statements, ranks, precisions and references in one
request.

## Selection

`wikidata-selection.tsv.gz`, one row per item and reason, with the current item (empty if deleted).

| Reason | Rule |
|---|---|
| `linked` | an item named as object in one of our datasets; detail: the dataset |
| `by-gnd`, `by-viaf`, `by-lc`, `by-geonames`, `by-isni` | an item that states an identifier our data names; detail: the identifier. A statement whose reference cites JudaicaLink (stated in or imported from Q132858785, or a reference URL in judaicalink.org) does not count (decision 0029) |
| `by-dbpedia` | the item of the English Wikipedia article of a DBpedia resource our data names; detail: the resource name |

## Data

Each record `data/wikidata/<Q>` has `owl:sameAs` the item and, from the best-ranked statements (preferred, else
normal; those citing JudaicaLink left out): `skos:prefLabel` (en, de, he, mul), the classes (`wdt:P31`), `foaf:Person`
for humans (Q5) and `schema:Place` for items with a GeoNames ID (other classes of places are left to record-classes),
`jl:birthDate`/`deathDate` in the precision Wikidata gives (year, month, day; coarser values left out, the calendar
as given), `wdt:P19`/`P20` and `jl:birthLocationURI`/`deathLocationURI` (the items of the places), the identifiers
GND, VIAF, LC, GeoNames, ISNI as IRIs in canonical form with Wikidata's normalized properties (`wdtn:`), NLI J9U,
YIVO, BHR and Encyclopedia of Russian Jewry as literals (`wdt:`), and the Wikipedia articles (en, de, he) as
`foaf:isPrimaryTopicOf`. The identifiers are stated as values, as Wikidata states them, not as `owl:sameAs`; the
linkset made from this dataset (`ls-wikidata`, decision 0029) decides on identity, and it uses these values,
including the identifiers of our sources (NLI J9U P8189, YIVO P8569, BHR P10405, Encyclopedia of Russian Jewry
P10278).

Replacements: a named item that was merged, `<old item> dcterms:isReplacedBy <new item>`; a named item that does not
exist any more, `<item> owl:deprecated true`.

## Run of 2026-10-16

102,769 items, 1,422,933 triples; items by reason (in brackets: not reached by a reason above): linked 82,530,
by-gnd 52,415 (13,448), by-viaf 77,160 (924), by-lc 56,967 (2,442), by-geonames 6,496 (2,578), by-isni 32,130 (37),
by-dbpedia 12,314 (831). 226 named items merged, 21 named items deleted. Statements citing JudaicaLink: none among the
identifiers; two others left out (the place of birth of Q5220790, the date of death of Q25490224). About a minute.

The queries (2026-10-16, about five hours in all, most of it waiting): the Query Service throttled (429) and broke
off answers (502/503, and once an answer of status 200 that ended in its time-out message, which `query.py` now
rejects), the API waited repeatedly for its replicas (maxlag). The answers are cached per value in the work dir, so a
later run asks only for new values; the ISNI values are 16 characters without spaces in Wikidata.

## Reproduction

**Reproducible** from the input. A new query run gives a new input and a new version.
