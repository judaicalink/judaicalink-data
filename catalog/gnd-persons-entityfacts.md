+++
slug = "gnd-persons-entityfacts"
title = "GND persons of hhkeydocs, nrwbibdjg and gba (DNB EntityFacts)"
author = "Kai Eckert"
date = "2026-10-12"
website = "https://hub.culturegraph.org/entityfacts/"
example = "http://data.judaicalink.org/data/gnd/100180930"
kind = "records"
method = ["lookup"]
namespaces = ["gnd"]
inputs = ["gnd-persons", "hhkeydocs", "nrwbibdjg", "gba"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/gnd-persons-entityfacts"
+++

GND records for the persons of hhkeydocs, nrwbibdjg and gba that gnd-persons does not have, from the DNB EntityFacts
service.

<!--more-->

The records are in the namespace of gnd-persons (`http://data.judaicalink.org/data/gnd/<GND number>`), so that a
person with a GND number has one record IRI in JudaicaLink whichever dataset brought it in. Names, life dates,
places, occupations, the biographical note and links to other authority files (VIAF, Wikidata, …), looked up by GND
number in DNB EntityFacts (answers of 2026-10-06). Links that EntityFacts gives to JudaicaLink IRIs in the `https` form
are normalised to `http`; a link of a record to itself is dropped.
