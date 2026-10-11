+++
slug = "compact-memory"
title = "Linking Compact Memory - Pages"
author = "Kai Eckert"
date = "2021-01-19"
namespaces = ["compact-memory"]
inputs = ["compact-memory-supp"]
stable = "2021-01-18"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/compact-memory"

[files]
"cm_tagme_pages.ttl.gz" = "Page metadata in RDF for Compact Memory, for pages where entity references have been found (624682 triples)."

[[versions]]
version = "2021-01-18"
issued = "2021-01-18"
author = "Marco Rovera"
graph = "http://data.judaicalink.org/data/compact-memory"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "cm_tagme_pages.ttl.gz"
  bytes = 3908853
  sha256 = "6c6bbedb82547dd4b06d8969760b312a03b0b7233b6b6620e334a8d69adb0874"

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the published version was not regenerated."
+++
Page metadata description in RDF for pages in Compact Memory where an entity mention has been found. The dataset describes pages, journals, journal issues and their relations, along with a pointer to the visual representation of each page in the Visual Library.

<!--more-->
