+++
slug = "corrections-links"
title = "Corrections of identity links"
author = "Kai Eckert"
date = "2026-10-12"
kind = "correction"
method = ["curated"]
inputs = ["interlinks", "dbpedia-persons", "gnd-persons", "ubffm-persons", "hhkeydocs", "nli-records", "ls-nli-legacy", "dbp-wiki-geo-linking", "rujen", "cm-entities"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/corrections-links"
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
