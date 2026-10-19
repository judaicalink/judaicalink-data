# wikidata: generator

The Wikidata items JudaicaLink uses (decision 0029), from answers of Wikidata kept in the inputs area.

## History

- 2026-10-16 (Kai Eckert): new dataset (run only, 102,769 items; never a version).
- 2026-10-19 (Kai Eckert): first version; the selection and the answers come from the cascade of the authority
  datasets (`jl cascade`, decision 0029). The items of Wikipedia articles come through the dataset dbpedia.

## Inputs

- `inputs:cascade/2026-10-19`, written by `lookup.py` in the cascade:
  - `wikidata-selection.tsv.gz`: the selection.
  - `entities.jsonl.gz`: the Wikidata API (`wbgetentities`, 50 items per request), the content of the selected
    items, one line per requested item, reduced to the labels (en, de, he, mul), the sitelinks (enwiki, dewiki,
    hewiki) and the statements of P31, P19, P20, P569, P570, P227, P214, P244, P1566, P213, P8189, P8569, P10405,
    P10278 (rank, value, and of the references only P248, P143, P854). A merged item is answered under its old id with
    `"redirect"`, a deleted one without `"entity"`.
  - `find-<P>.rq` / `.tsv`: the Wikidata Query Service, which items state an identifier the cascade selected (P227
    GND, P214 VIAF, P244 LC, P1566 GeoNames, P213 ISNI), in batches of 3,000 values.

`lookup.py` asks online, with caches per item and per value in the work dir (`work/wikidata-query/`), so a later
cascade asks only for what is new: resolve (a merged item gives the item it redirects to, a deleted one none), links
(the identity statements as the dataset writes them, and the English and German articles), search (the items that
state a GND, VIAF, LC, GeoNames or ISNI number), and as seeds the items that state the identifier of a record of ours
(YIVO P8569, BHR P10405, Encyclopedia of Russian Jewry P10278; all items with these properties asked once, matched as
in ls-wikidata). The Query Service is used only for these lookups by identifier: it throttles and times out on
content queries, and the API answers 50 items with all their statements, ranks, precisions and references in one
request.

## Selection

`wikidata-selection.tsv.gz`, one row per item and reason, with the current item (empty if deleted).

| Reason | Rule |
|---|---|
| `linked` | an item named as object in one of our datasets, or by a declared identity statement of another authority dataset (decision 0032); detail: the dataset |
| `replaces` | the item a selected item was merged into; detail: the selected item |
| `by-gnd`, `by-viaf`, `by-lc-names`, `by-geonames`, `by-isni` | an item that states an identifier the cascade selected; detail: the identifier. A statement whose reference cites JudaicaLink (stated in or imported from Q132858785, or a reference URL in judaicalink.org) does not count (decision 0029) |
| `by-yivo`, `by-bhr`, `by-rujen` | an item that states the identifier of a record of ours (YIVO P8569, BHR P10405, Encyclopedia of Russian Jewry P10278); detail: the record |

## Data

Each record `data/wikidata/<Q>` has `owl:sameAs` the item and, from the best-ranked statements (preferred, else
normal; those citing JudaicaLink left out): `skos:prefLabel` (en, de, he, mul), the classes (`wdt:P31`), `foaf:Person`
for humans (Q5) and `schema:Place` for items with a GeoNames ID (other classes of places are left to record-classes),
`jl:birthDate`/`deathDate` in the precision Wikidata gives (year, month, day; coarser values left out, the calendar
as given), `wdt:P19`/`P20` and `jl:birthLocationURI`/`deathLocationURI` (the items of the places), the identifiers
GND, VIAF, LC, GeoNames, ISNI as IRIs in canonical form with Wikidata's normalized properties (`wdtn:`), NLI J9U,
YIVO, BHR and Encyclopedia of Russian Jewry as literals (`wdt:`), and the Wikipedia articles (en, de, he) as
`foaf:isPrimaryTopicOf`. The identifiers are stated as values, as Wikidata states them, not as `owl:sameAs`; which of
them state identity is declared in the catalogue entry (decision 0032), and the linksets (`ls-gnd`, …,
`ls-wikidata`) decide on the links.

Replacements: a named item that was merged, `<old item> dcterms:isReplacedBy <new item>`; a named item that does not
exist any more, `<item> owl:deprecated true`.

## Version 2026-10-19

89,457 items, 1,232,811 triples; items by reason (in brackets: not reached by a reason above): linked 77,180,
replaces 35 (0), by-gnd 61,202 (50), by-viaf 83,522 (11,043), by-lc-names 60,387 (38), by-geonames 7,963 (865),
by-isni 61,897 (28); selected by a record of ours: by-yivo 1,447, by-bhr 1,050, by-rujen 28. 855 named items merged,
18 deleted. No identifier statement cites JudaicaLink. About 15 seconds (the queries are made by the cascade).

## Reproduction

**Reproducible** from the input. A new cascade gives a new input and a new version (`docs/process.md`, 2a).
