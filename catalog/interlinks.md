+++
slug = "interlinks"
title = "Encyclopedia Interlinks"
author = "Kai Eckert"
date = "2018-02-15"
namespaces = ["interlinks"]
stable = "2018-07-18"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/interlinks"

[files]
"interlinks-04-enriched-09.ttl.gz" = "Links between JudaicaLink persons."

[[versions]]
version = "2018-07-18"
issued = "2018-07-18"
author = ["Kai Eckert", "Maral Dadvar"]
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "interlinks.n3.gz"
  bytes = 1903
  sha256 = "c9935e962444296c896ee094226ff4641532c8fc72d0c54bb8e9da7e797cc466"

  [[versions.files]]
  path = "interlinks-04-enriched-09.ttl.gz"
  bytes = 35667
  sha256 = "06363cc99920fb6eb2aed740b209a5514ab80867ec053774499c09bc91839bad"

  [[versions.files]]
  path = "interlinks-meta.ttl.gz"
  bytes = 1983
  sha256 = "e7fa836ad3770939e8d1a21071d2da2b6c4923628cee23d7006d2bce6624f0b3"
  triples = 70

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the published version was not regenerated."

[[changelog]]
date = "2018-02-13"
author = "Maral Dadvar"
text = "Interlinks between persons added (first enriched interlinks)."

[[changelog]]
date = "2017-02-15"
author = "Kai Eckert"
text = "First version (interlinks.n3.gz)."
+++

Links between JudaicaLink entities and persons. 
<!--more-->

The first file includes only a very preliminary example for entity linking. This dataset so far contains only links between [Rujen](/datasets/rujen) and [Yivo](/datasets/yivo).

The links are created based on [DBpedia](http://www.dbpedia.org/), i.e., if two entities are linked to the same DBpedia concept (potentially via different language editions), they are considered the same.

The second file contains links between the persons in all the existing datasets. For each group the transitive closure is also created and therefore each person is also interlinked to the external resources. 

Counts in the former catalogue entry: links: 152 entities. 700 person groups interlinked. Maximum 24 resource per group.
