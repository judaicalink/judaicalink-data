+++
slug = "judaicalink-vocabulary"
title = "JudaicaLink dataset vocabulary"
author = "Kai Eckert"
date = "2026-10-11"
example = "http://data.judaicalink.org/datasets/vocabulary/method/ai-generated"
kind = "vocabulary"
method = ["curated"]
stable = "2026-10-11-2"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/judaicalink-vocabulary"

[[versions]]
version = "2026-10-11-2"
issued = "2026-10-11"
author = "Kai Eckert"
commit = "9423f89947f1e7329d093043881336af629fa490"

  [[versions.files]]
  path = "judaicalink-vocabulary.ttl.gz"
  bytes = 1758
  sha256 = "792db7d25ca07fd80f892e027369c3e7d0cf84a2ef1ac6832f3101a9781c884b"
  triples = 126

  [[versions.files]]
  path = "judaicalink-vocabulary-meta.ttl.gz"
  bytes = 1527
  sha256 = "cfb500e8a38060854dc34ee1c276ef2bbc57394bd58c8e08e23a176ad3cfb276"
  triples = 55

[[versions]]
version = "2026-10-11"
issued = "2026-10-11"
author = "Kai Eckert"
commit = "8c2c00b2f183d5c4a9c50c4819ed4b495b4efe1c"

  [[versions.files]]
  path = "judaicalink-vocabulary.ttl.gz"
  bytes = 1492
  sha256 = "9759e9a13bc7a4377547340ec08547f02ddeffc9ee934e6eadf2da57ea780aa1"
  triples = 111

  [[versions.files]]
  path = "judaicalink-vocabulary-meta.ttl.gz"
  bytes = 1519
  sha256 = "77c827dc7c2d19c7d4fe3121ab9e12e8e4fd8cd1f2b508516556e022f6a63d95"
  triples = 55

[[changelog]]
date = "2026-10-12"
version = "2026-10-11-2"
author = "Kai Eckert"
text = "machine-translation added; lookup only by identifier, name matching rule-based; the automated methods and their broader concept method/automated."

[[changelog]]
date = "2026-10-11"
version = "2026-10-11"
author = "Kai Eckert"
text = "First version: the values of kind and method of 2026-10-11 (7 kinds, 8 methods)."
+++

The kinds of JudaicaLink datasets and the methods by which they are made, as SKOS concepts.

<!--more-->

The metadata of every dataset version (its `-meta` file) states what kind of dataset it is (records, complement,
linkset, entity pages, ontology, vocabulary, support data) and how its statements were made (curated, scraped,
converted, deterministic, rule-based, lookup, statistical, AI-generated) as `dcterms:type`, with IRIs
`http://data.judaicalink.org/datasets/vocabulary/kind/<kind>` and
`http://data.judaicalink.org/datasets/vocabulary/method/<method>`. This dataset defines these values. It is
generated from `catalog/vocabulary.toml` in judaicalink-data, which is also the list of values the catalogue
accepts.
