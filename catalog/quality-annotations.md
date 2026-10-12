+++
slug = "quality-annotations"
title = "Quality annotations for the JudaicaLink datasets"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["rule-based"]
namespaces = ["quality-annotations"]
inputs = ["bhr", "dbpedia-persons", "djh", "epidat", "footprints", "geo-enriched", "gnd-persons", "gnd-persons-entityfacts", "haskala", "hhkeydocs", "hirsch-family", "jre", "nli-records", "sosy", "ubffm-persons", "compact-memory", "geo-coordinates", "nrwbibdjg"]
stable = "2026-10-12"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/quality-annotations"

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "0413afaf730617f597a8de2c92865fed1e6e736d"

  [[versions.files]]
  path = "quality-annotations.ttl.gz"
  bytes = 22549
  sha256 = "2bd5019d95cc16ea57cda6a92a5d179ba29e6934b1acb12845fcb8f8a207a2f5"
  triples = 3954

  [[versions.files]]
  path = "quality-annotations-meta.ttl.gz"
  bytes = 2659
  sha256 = "ae9ef5f051c2a5abee62766f9614d4c2d22d29b6567e34e9e29c365224b7caf5"
  triples = 113

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: quality annotations about the data (dates left out by records-normalized, with the reason; issues of Compact Memory in isolated years; problems of single versions), from quality-annotations of kg-complements (decision 0020)."
+++

Problems in the data that cannot be fixed by adding facts, as quality annotations (W3C Data Quality Vocabulary and
Web Annotation): dates that could not be normalised, issues with an unlikely year, errors of single versions.

<!--more-->

Each annotation (`dqv:QualityAnnotation`, `oa:Annotation`) names its target with `oa:hasTarget`, describes the
problem in `oa:bodyValue` and gives its kind in `dcterms:type`:

- **date**: a birth or death date of a record that `records-normalized` could not normalise, with the reason (the
  same rules: a range, a bound, a negative year, …), records whose death date is before their birth date, and issues
  of Compact Memory in a
  year more than 15 years away from every other year of their journal (probably a typo in the source metadata);
- **vocabulary**, **datatype**, **syntax**, **data error**: problems of one version of a dataset, targeted at the
  version (`datasets/<slug>/<version>`): the misspelt property `jl:occpation`, IRIs as values of `jl:occupation`,
  `dcterms:created` as a plain string, RDF-star statements, `jl:lat` and `jl:lon` swapped; and problems found by
  hand.

The annotations are about records and versions, never about entity pages.
