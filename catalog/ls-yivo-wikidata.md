+++
slug = "ls-yivo-wikidata"
title = "YIVO Encyclopedia articles linked to Wikidata"
author = "Kai Eckert"
date = "2026-10-12"
example = "http://data.judaicalink.org/data/yivo/abramovich_rafail"
kind = "linkset"
method = ["lookup"]
inputs = ["yivo"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-yivo-wikidata"
+++

The articles of the YIVO Encyclopedia of Jews in Eastern Europe (dataset yivo) linked to their Wikidata items.

<!--more-->

Wikidata names the YIVO article of an item with the property P8569 (YIVO Encyclopedia of Jews in Eastern Europe ID).
Every yivo record whose article has exactly one Wikidata item gets `owl:sameAs` that item; articles with several
items are left out. The links join the YIVO articles with the other records about the same person, place or
organisation on the entity pages.
