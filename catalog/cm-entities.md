+++
slug = "cm-entities"
title = "Compact Memory entities: presence and Wikidata"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["deterministic", "lookup"]
inputs = ["cm-tagme", "dbpedia-persons", "interlinks"]
stable = "2026-10-12"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/cm-entities"

[files]
"cm-entities-presence.ttl.gz" = "For every entity linked in Compact Memory: mentions, pages, first and last year, journals, the journal with the most mentions."
"cm-entities-wikidata.ttl.gz" = "For the entities that no other dataset names: Wikidata item, labels (de, en, he), type, coordinates, GND, VIAF and GeoNames IDs."

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "e6969f71110b36ef1d45e68887fae59b0f081038"

  [[versions.files]]
  path = "cm-entities-presence.ttl.gz"
  bytes = 119834
  sha256 = "aeb7add03b6b3c482750a8a8d10decc3a76dba2ef953aec73827c5f69e4e777e"
  triples = 32662

  [[versions.files]]
  path = "cm-entities-wikidata.ttl.gz"
  bytes = 273155
  sha256 = "8e0d443a9eaa07fe89e68e51c6d35e642e0c034328058d930ada90a0fea20c5c"
  triples = 40303

  [[versions.files]]
  path = "cm-entities-meta.ttl.gz"
  bytes = 3089
  sha256 = "a651b2a7d626132cddeee2bd5bde04954223209dbe50834bc88ed3ab361462d2"
  triples = 81

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: presence and Wikidata data of the Compact Memory entities (cm-entities-presence and cm-entities-wikidata of kg-complements, decision 0020)."
+++

What is known about the entities (mainly persons and places) that were linked in the Compact Memory full text by
TagMe (cm-tagme): how often and when they are mentioned, and, for those that no other dataset names, their data from
Wikidata.

<!--more-->

Presence: for every entity, the number of mentions and pages, the first and last year of mention, the number of
journals and the journal with the most mentions; years and journals come from the full-text index via the page. The
counts are exact for the TagMe links, which are themselves automatic (cm-tagme).

Wikidata: for the entities that no other dataset names, the Wikidata item, found through the German Wikipedia title in
the entity IRI (following redirects); labels in German, English and Hebrew; the type (person, or place if the item has
coordinates); coordinates; and GND, VIAF and GeoNames identifiers from Wikidata. The statements are about the entities
(the records of cm-tagme), not about entity pages.
