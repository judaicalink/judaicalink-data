+++
slug = "quality-annotations"
title = "Quality annotations for the JudaicaLink datasets"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["rule-based"]
namespaces = ["quality-annotations"]
inputs = ["bhr", "dbpedia-persons", "djh", "epidat", "footprints", "geo-enriched", "gnd-persons", "gnd-persons-entityfacts", "haskala", "hhkeydocs", "hirsch-family", "jre", "nli-records", "sosy", "ubffm-persons", "compact-memory", "geo-coordinates", "nrwbibdjg"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/quality-annotations"
+++

Problems in the data that cannot be fixed by adding facts, as quality annotations (W3C Data Quality Vocabulary and
Web Annotation): dates that could not be normalised, issues with an unlikely year, errors of single versions.

<!--more-->

Each annotation (`dqv:QualityAnnotation`, `oa:Annotation`) names its target with `oa:hasTarget`, describes the
problem in `oa:bodyValue` and gives its kind in `dcterms:type`:

- **date**: a birth or death date of a record that `records-normalized` could not normalise (the same rules; for
  the dates of footprints written as Python dictionaries, the EDTF date in them), and issues of Compact Memory in a
  year more than 15 years away from every other year of their journal (probably a typo in the source metadata);
- **vocabulary**, **datatype**, **syntax**, **data error**: problems of one version of a dataset, targeted at the
  version (`datasets/<slug>/<version>`): the misspelt property `jl:occpation`, IRIs as values of `jl:occupation`,
  `dcterms:created` as a plain string, RDF-star statements, `jl:lat` and `jl:lon` swapped; and problems found by
  hand.

The annotations are about records and versions, never about entity pages.
