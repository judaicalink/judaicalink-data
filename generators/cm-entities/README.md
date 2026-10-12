# cm-entities: generator

Presence and Wikidata data of the entities linked in Compact Memory (new dataset, decision 0020: cm-entities-presence
and cm-entities-wikidata of kg-complements combined).

## History

- 2026-10-05/06 (Kai Eckert): `cm_entities_presence` (`datasets_deterministic.py`) and `cm_entities_wikidata`
  (`datasets_algorithmic.py`) in kg-complements; the Wikipedia and Wikidata APIs were queried on 2026-10-06 and their
  answers cached; outputs in `dumps-additions/`, never published.

## Framework generator

`generate.py` (2026-10-12): a port of both without changes to their logic. Inputs: `cm-tagme/2021-01-18` (the
references), the full-text bundle `inputs:compact-memory/fulltext-2026-10-05-v2` (date and journal per page), the API
cache `inputs:web-caches/api-cache-2026-10-06` (195 answers used; a missing answer is an error, not a live request),
and `dbpedia-persons/2018-10-24` and `interlinks/2018-07-18` for "entities that no dataset names". The builder of 2026
checked that against every graph of the endpoint; on 2026-10-12 all stable versions of the catalogue were checked:
only these two name any of the 5,445 entities (586 and 89), which gives the same 4,859 entities. Writes
`cm-entities-presence.ttl.gz` and `cm-entities-wikidata.ttl.gz` (40,303 triples, identical to the kg-complements
output). About one minute.

The presence data is stated as `jl:CorpusPresence` nodes (decided 2026-10-12, judaicalink-ontology PR 18): instead of
`jl:cmMentionCount` etc. on the entity, one node per entity, `data/cm-entities/presence/<entity IRI after data/>`, with
`jl:entity`, `jl:corpus` (`data/compact-memory/corpus`) and `jl:mentionCount`, `jl:pageCount`, `jl:firstMentionYear`,
`jl:lastMentionYear`, `jl:journalCount`, `jl:mostFrequentJournal`; the same numbers as the kg-complements output
(32,662 triples there).
