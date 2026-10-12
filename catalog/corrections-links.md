+++
slug = "corrections-links"
title = "Corrections of identity links"
author = "Kai Eckert"
date = "2026-10-12"
stable = "2026-10-12"
kind = "correction"
method = ["curated"]
inputs = ["interlinks", "2014links", "dbpedia-persons", "gnd-persons", "ubffm-persons", "hhkeydocs", "nli-records", "ls-nli-legacy", "dbp-wiki-geo-linking", "rujen", "cm-entities"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/corrections-links"

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "dc401a969c2fdafccdfd2e43afb782c220801a98"

  [[versions.files]]
  path = "corrections-links-deletions.ru.gz"
  bytes = 2723
  sha256 = "a340acd302cd68d5926e402c05eac48cbf43cb6e724c6d8cf32632427d4909b0"

  [[versions.files]]
  path = "corrections-links.ttl.gz"
  bytes = 177
  sha256 = "8f7313301125a7a582ccc03e222e881c627c3c4c64553a514032de32a48a481e"
  triples = 3

  [[versions.files]]
  path = "corrections-links-meta.ttl.gz"
  bytes = 2297
  sha256 = "759a9e5084c4ce88c6da4a4c4df19f183ec84118a11ea76a9aee171b48df0634"
  triples = 108

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: 80 wrong identity links deleted in 11 datasets (persons and places joined with others), 3 places of rujen typed as places; found with the entity-page closure (decisions 0022, 0023)."
+++

Corrections of identity links (`owl:sameAs`, GND numbers, types) that join different persons or places: Sherira Gaon
and his son Hai Gaon, the two Otto Warburgs, Simeon bar Yochai and Simeon ben Gamliel II, works of the NLI and their
authors, and others. A correction dataset (decision 0023): its deletions are applied after all other datasets.

<!--more-->

- `corrections-links-deletions.ru.gz`: the triples to delete from every graph that contains them, as SPARQL 1.1 Update
  in the fixed form of decision 0023, with the evidence for each block as a comment.
- `corrections-links.ttl.gz`: the triples added (the class `jl:Place` for three places of rujen that were typed as
  persons).

Found by checking the groups of the entity-page closure (decision 0022) that contain several Wikidata items or records
of incompatible classes, and checked one by one (Wikidata, id.loc.gov, the records themselves). Systematic errors of a
dataset are fixed by a new version of it instead (decision 0024).
