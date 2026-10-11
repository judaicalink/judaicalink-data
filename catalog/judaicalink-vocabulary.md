+++
slug = "judaicalink-vocabulary"
title = "JudaicaLink dataset vocabulary"
author = "Kai Eckert"
date = "2026-10-11"
example = "http://data.judaicalink.org/datasets/vocabulary/method/ai-generated"
kind = "vocabulary"
method = ["curated"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/judaicalink-vocabulary"
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
