+++
slug = "ls-footprints-viaf"
title = "Footprints persons linked to VIAF, judged one by one"
author = "Kai Eckert"
date = "2026-10-26"
example = "http://data.judaicalink.org/data/footprints/person/1371"
kind = "linkset"
method = ["rule-based", "llm-judged"]
inputs = ["footprints", "record-classes", "viaf"]

[identity]   # the properties that state identity, and towards which sources (decision 0032)
"jl:sameAs" = ["viaf"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-footprints-viaf"
+++

The VIAF numbers that Footprints gives its persons, linked to the JudaicaLink record of the cluster in the dataset
viaf where rules and a large language model judged them correct: automatic linking, not checked by people.

<!--more-->

Footprints names a VIAF cluster for some of its persons. On a sample these links are 94% correct, below the quality
threshold of JudaicaLink, so the linkset of all VIAF links (ls-viaf) leaves them out (decision 0032). Here every link
was judged on its own (decision 0037): left out are clusters the dataset viaf does not have and links between a
person and a work; then a language model read what both sides say (names, life dates, the roles, books, dates and
places of the person in Footprints, the GND record and Wikidata item of the cluster) and judged each link correct,
wrong or undecidable. Only the links judged correct are in the linkset; the file of decisions gives the outcome and
the reason for every link.
