+++
slug = "cm-entities"
title = "Compact Memory entities: presence and Wikidata"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["deterministic", "lookup"]
namespaces = ["cm-entities"]
example = "http://data.judaicalink.org/data/cm-entities/presence/dbpedia/A._E._Housman"
inputs = ["cm-tagme", "dbpedia-persons", "interlinks"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/cm-entities"

[files]
"cm-entities-presence.ttl.gz" = "For every entity linked in Compact Memory, its presence in the corpus (jl:CorpusPresence): mentions, pages, first and last year, journals, the journal with the most mentions."
"cm-entities-wikidata.ttl.gz" = "For the entities that no other dataset names: Wikidata item, labels (de, en, he), type, coordinates, GND, VIAF and GeoNames IDs."

+++

What is known about the entities (mainly persons and places) that were linked in the Compact Memory full text by
TagMe (cm-tagme): how often and when they are mentioned, and, for those that no other dataset names, their data from
Wikidata.

<!--more-->

Presence: for every entity, a `jl:CorpusPresence` that links it (`jl:entity`) with the corpus Compact Memory
(`jl:corpus`, `http://data.judaicalink.org/data/compact-memory/corpus`) and states the number of mentions and pages,
the first and last year of mention, the number of journals and the journal with the most mentions; years and journals
come from the full-text index via the page. The node IRIs are
`http://data.judaicalink.org/data/cm-entities/presence/<the entity IRI after data/>`. The counts are exact for the
TagMe links, which are themselves automatic (cm-tagme).

Wikidata: for the entities that no other dataset names, the Wikidata item, found through the German Wikipedia title in
the entity IRI (following redirects); labels in German, English and Hebrew; the type (person, or place if the item has
coordinates); coordinates; and GND, VIAF and GeoNames identifiers from Wikidata. The statements are about the entities
(the records of cm-tagme), not about entity pages.
