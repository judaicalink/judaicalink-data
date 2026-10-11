+++
slug = "judaicalink-agents"
title = "JudaicaLink agents"
author = "Kai Eckert"
date = "2026-10-11"
example = "http://data.judaicalink.org/datasets/agents/persons/1"
kind = "support"
method = ["curated"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/judaicalink-agents"
+++

The persons and software agents named in the metadata of the JudaicaLink datasets.

<!--more-->

The metadata of every dataset version (its `-meta` file) names the persons and programs that made it by IRI
only: persons as `http://data.judaicalink.org/datasets/agents/persons/<n>`, numbered in sequence, software as
`http://data.judaicalink.org/datasets/agents/software/<name>`. This dataset gives their names. It is generated
from the registry `catalog/agents.toml` in judaicalink-data. If a person does not want to be named, the name is
removed here; the IRI stays.
