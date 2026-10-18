+++
slug = "wikidata"
title = "Wikidata: the items JudaicaLink uses"
author = "Kai Eckert"
date = "2026-10-16"
website = "https://www.wikidata.org/"
example = "http://data.judaicalink.org/data/wikidata/Q559622"
kind = "authority"
method = ["converted", "lookup"]
namespaces = ["wikidata"]

[identity]   # the properties that state identity, and towards which sources (decision 0032)
"wdtn:P227" = ["gnd"]
"wdtn:P214" = ["viaf"]
"wdtn:P244" = ["lc-names"]
"wdtn:P1566" = ["geonames"]
"wdtn:P213" = ["isni"]
"foaf:isPrimaryTopicOf" = ["wikipedia-en", "wikipedia-de"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"
statement = "https://web.archive.org/web/20261006200927/https://www.wikidata.org/wiki/Wikidata:Licensing"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/wikidata"
+++

The items of Wikidata that JudaicaLink uses: every item one of our datasets links, and the items that state an
identifier our data names (GND, VIAF, LC, GeoNames, ISNI) or are the English Wikipedia article of a DBpedia resource
we link.

<!--more-->

Wikidata is a knowledge base that anyone can edit. Many of its statements are added by bots, identifiers among
them (for example from VIAF), and references are optional, so an item's identifiers are only as reliable as their
sources; errors are reported to Wikidata. Statements that cite JudaicaLink as their source are left out: they most
likely come from our own data and are never evidence for our links (decision 0029).

The dataset is made from answers of the Wikidata Query Service (which items state an identifier) and of the
Wikidata API (the content of the items), kept with their queries in the inputs area; their date is in the metadata
of each version. Each record keeps the item's labels (en, de, he), classes, dates and places of birth and death, its
identifiers (GND, VIAF, LC, GeoNames, ISNI as IRIs in canonical form; NLI, YIVO, BHR, Encyclopedia of Russian Jewry as
values) and its Wikipedia articles (en, de, he). Merged items are stated with `dcterms:isReplacedBy`, deleted ones
that our data names with `owl:deprecated`.

`wikidata-selection.tsv.gz` lists why each item is included: one row per item and reason (linked by a dataset, or
reached by an identifier), with the current item.
