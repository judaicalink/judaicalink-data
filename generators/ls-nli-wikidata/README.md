# ls-nli-wikidata: generator

The records of nli-records linked to their Wikidata items, through the VIAF and LC numbers the records carry.

## History

- 2026-10-15 (Kai Eckert): new linkset. The NLI publishes no authority dump that we could read again (its website and
  API need a browser check or a key); Wikidata states the NLI J9U ID (P8189) for about 890,000 items, but the 2019
  export of nli-records has no NLI control number. The join goes through the numbers the records have: VIAF (field
  901, 182,553 records) and LC (field 010, 54,140).

## Inputs

- `nli-records/2026-10-12`: the records and their `owl:sameAs` links to `viaf.org/viaf/<n>` and
  `id.loc.gov/authorities/names/<n>`.
- `inputs:web-caches/wikidata-nli-2026-10-15`: the answers of the Wikidata Query Service for all these numbers,
  `p214.tsv` (VIAF ID) and `p244.tsv` (LC authority ID), one row per number and item, with the queries `p214.rq` and
  `p244.rq` (`VALUES_` stands for the numbers, sent in batches of 4,000). Made by `query.py`.

## Rule

A record gets `owl:sameAs` its item only when the match is unique in both directions: its numbers lead to exactly one
item, and no other record leads to that item. Left out and named in the run log: records whose numbers lead to
several items (a number on several items, or VIAF and LC pointing to different items), and items reached from
several records (records sharing a VIAF number have hash IRIs in nli-records, and Wikidata may hold one item for
what VIAF splits). With Wikidata's VIAF and LC statements as the only evidence, a wrong VIAF cluster on either side
passes; the names are not compared.

## Reproduction

**Reproducible** from the input (about one minute). A new query gives a new input and a new version.
