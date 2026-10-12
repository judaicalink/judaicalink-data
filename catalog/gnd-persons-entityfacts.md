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
stable = "2026-10-12"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/gnd-persons-entityfacts"

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "61ec4427341856190ac3f2b3eae3aa7993bfb41f"

  [[versions.files]]
  path = "gnd-persons-entityfacts.ttl.gz"
  bytes = 178370
  sha256 = "2d0123d5bdf2533af5d4ac2634a3ad69724392fe2b0d854329785602c27a83c6"
  triples = 19053

  [[versions.files]]
  path = "gnd-persons-entityfacts-meta.ttl.gz"
  bytes = 2230
  sha256 = "f3ef8f9925931bddb255b7bcc64667a7f744803e8468af45d5347427021a6fc8"
  triples = 74

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: GND records from DNB EntityFacts for the persons of hhkeydocs, nrwbibdjg and gba that gnd-persons lacks (decision 0020); https links to JudaicaLink normalised, self-links dropped."
+++

GND records for the persons of hhkeydocs, nrwbibdjg and gba that gnd-persons does not have, from the DNB EntityFacts
service.

<!--more-->

The records are in the namespace of gnd-persons (`http://data.judaicalink.org/data/gnd/<GND number>`), so that a
person with a GND number has one record IRI in JudaicaLink whichever dataset brought it in. Names, life dates,
places, occupations, the biographical note and links to other authority files (VIAF, Wikidata, …), looked up by GND
number in DNB EntityFacts (answers of 2026-10-06). Links that EntityFacts gives to JudaicaLink IRIs in the `https` form
are normalised to `http`; a link of a record to itself is dropped.
