+++
slug = "judaicalink-vocabulary"
title = "JudaicaLink dataset vocabulary"
author = "Kai Eckert"
date = "2026-10-11"
example = "http://data.judaicalink.org/datasets/vocabulary/method/ai-generated"
kind = "vocabulary"
method = ["curated"]
stable = "2026-10-11"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/judaicalink-vocabulary"

[[versions]]
version = "2026-10-11"
issued = "2026-10-11"
author = "Kai Eckert"
commit = "156e60ef6a76d46b2e7f4197083bdeee2601428c"

  [[versions.files]]
  path = "judaicalink-vocabulary.ttl.gz"
  bytes = 1756
  sha256 = "752f5645270c1649ccab61f836adba48955465a6e7254178aa9dd97c7c615c73"
  triples = 126

  [[versions.files]]
  path = "judaicalink-vocabulary-meta.ttl.gz"
  bytes = 1521
  sha256 = "2fb61824498becf5ad235c9bb966a650e674542fbf8b69ffbfbc069480489432"
  triples = 55

[[changelog]]
date = "2026-10-12"
version = "2026-10-11"
author = "Kai Eckert"
text = "First version: 7 kinds, 9 methods, and the derived concept method/automated."
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
