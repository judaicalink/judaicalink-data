+++
slug = "ls-wikidata"
title = "Links to the Wikidata records"
author = "Kai Eckert"
date = "2026-10-18"
example = "http://data.judaicalink.org/data/yivo/abramovich_rafail"
kind = "linkset"
method = ["deterministic", "rule-based"]
inputs = ["wikidata", "yivo", "bhr", "rujen", "dbpedia-persons"]
replaces = ["ls-yivo-wikidata"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-wikidata"
+++

Every JudaicaLink record that is a Wikidata item, linked to the JudaicaLink record of the current item in the
dataset wikidata.

<!--more-->

The links come from the Wikidata identifiers our datasets and the other authority datasets state, resolved through
the replacements Wikidata states (dataset `wikidata`), and from the identifiers of our sources that Wikidata states:
the articles of the YIVO Encyclopedia, the Biographisches Portal der Rabbiner and the Encyclopedia of Russian Jewry,
and the English Wikipedia articles of the DBpedia persons. These are linked only where the match is unique in both
directions. The links join the records of different datasets on the entity pages (decision 0029).
