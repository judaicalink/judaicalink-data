+++
slug = "gnd-persons-entityfacts"
title = "GND persons of hhkeydocs, nrwbibdjg and gba (DNB EntityFacts)"
author = "Kai Eckert"
date = "2026-10-12"
website = "https://hub.culturegraph.org/entityfacts/"
example = "http://data.judaicalink.org/data/gnd/100180930"
stable = "2026-10-12"
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

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "31d1970e78896363a98c25161305a67d0d8a8fd2"

  [[versions.files]]
  path = "gnd-persons-entityfacts.ttl.gz"
  bytes = 177847
  sha256 = "bb81e6c05aab03e7fdff23e745becc6495d070562724d1e2231576272ab06a11"
  triples = 19007

  [[versions.files]]
  path = "gnd-persons-entityfacts-meta.ttl.gz"
  bytes = 2247
  sha256 = "be85dea9ec6a34f227f32889ed8c525f73d2eb48be397f04cac8547e61d04105"
  triples = 74

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: GND records (DNB EntityFacts) for the persons of hhkeydocs, nrwbibdjg and gba that gnd-persons lacks (gnd-persons-entityfacts of kg-complements, decision 0020); https self-links dropped, template links dropped, the corrections of corrections-links applied."
+++

GND records for the persons of hhkeydocs, nrwbibdjg and gba that gnd-persons does not have, from the DNB EntityFacts
service.

<!--more-->

The records are in the namespace of gnd-persons (`http://data.judaicalink.org/data/gnd/<GND number>`), so that a
person with a GND number has one record IRI in JudaicaLink whichever dataset brought it in. Names, life dates,
places, occupations, the biographical note and links to other authority files (VIAF, Wikidata, …), looked up by GND
number in DNB EntityFacts (answers of 2026-10-06). Links that EntityFacts gives to JudaicaLink IRIs in the `https` form
are normalised to `http`; a link of a record to itself is dropped.
