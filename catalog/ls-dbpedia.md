+++
slug = "ls-dbpedia"
title = "Links to the Wikipedia articles"
author = "Kai Eckert"
date = "2026-10-18"
example = "http://data.judaicalink.org/data/bhr/1"
kind = "linkset"
method = ["deterministic"]
inputs = ["dbpedia"]

[identity]   # the properties that state identity, and towards which sources (decision 0032)
"jl:sameAs" = ["wikipedia-en", "wikipedia-de"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ls-dbpedia"
+++

Every JudaicaLink record that refers to an English or German Wikipedia article (or its DBpedia resource), linked to
the JudaicaLink record of the current article in the dataset dbpedia.

<!--more-->

An old title is followed to the current article (Wikipedia renames articles; decision 0031). A title that no longer
exists, or that the dataset dbpedia does not have, is left out. These links join the records of different datasets
on the entity pages (decision 0029).
