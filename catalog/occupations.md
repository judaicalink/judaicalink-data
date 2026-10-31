+++
slug = "occupations"
title = "Occupations"
author = "Kai Eckert"
date = "2025-12-18"
example = "http://data.judaicalink.org/data/occupation/Rabbiner"
namespaces = ["occupation"]
kind = "vocabulary"
method = ["converted", "rule-based", "curated"]
inputs = ["gnd", "records-normalized", "bhr", "sosy", "dbpedia"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/occupations"

[[changelog]]
date = "2025-12-18"
author = "Benjamin Schnabel"
text = "Entry and generator added (judaicalink-generators); no dump of this dataset was found."

[[changelog]]
date = "2026-10-31"
author = "Kai Eckert"
text = "A new generator: the occupations the data uses, as concepts. The GND subject headings that gnd names as occupations, and the occupation IRIs of the older datasets, which nothing described, linked to them. CC0 like the rest of the data."
+++

The occupations of JudaicaLink as concepts. All statements about occupations are in this dataset; the other datasets
only link to them.
<!--more-->

**GND occupations.** The GND names the occupations of persons with its subject headings. The dataset `gnd` links its
records to them (`jl:occupationURI`); this dataset describes them, with the broader headings up to the top: German
preferred and variant names (`skos:prefLabel`, `skos:altLabel`), the broader terms (`skos:broader`) and the GND subject
categories. The headings keep the GND's IRIs.

**Older occupation IRIs.** The datasets of 2018 made occupation IRIs from names, e.g.
`http://data.judaicalink.org/data/occupation/Rabbiner` (the GND's German names, gnd-persons) and
`http://data.judaicalink.org/data/occupation/musician` (English DBpedia categories, dbpedia-persons). records-normalized,
bhr, sosy and dbpedia still state them. Each gets its name with its language and a link to its GND heading
(`skos:exactMatch`): German names by the heading of that name, or of that variant name; English names by a table
chosen by hand. Mohel and Rebbetzin have no GND heading.
