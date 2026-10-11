+++
slug = "compact-memory-supp"
title = "Compact Memory page metadata"
author = "Kai Eckert"
date = "2021-01-19"
kind = "support"
stable = "2021-01-19"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/compact-memory-supp"

[files]
"CM_Seiten_Metadaten.csv.gz" = "Original metadata (pagewise) for Compact Memory."

[[versions]]
version = "2021-01-19"
issued = "2021-01-19"
author = "Marco Rovera"
description = "The original page metadata of the Visual Library (input of cm-structure and cm-journals); the pickle file of that catalogue state duplicated compact-memory and is not kept."

  [[versions.files]]
  path = "CM_Seiten_Metadaten.csv.gz"
  bytes = 13111336
  sha256 = "7affff32c1da8451ffc536db0cb526d39b09848dfcb59fa70b820493616fcd08"

  [[versions.files]]
  path = "compact-memory-supp-meta.ttl.gz"
  bytes = 1551
  sha256 = "cc1f733552c48b77006908152920f3f9c1f5367804d0c2fced7ccbe2bd852aaa"
  triples = 49

[[changelog]]
date = "2025-12-31"
author = "Benjamin Schnabel"
text = "The original xlsx export and the conversion notebook added to the workflow repository."
+++
Support data for Compact Memory - JL linking (pages).

<!--more-->
