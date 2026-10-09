+++
slug = "compact-memory-supp"
title = "Linking Compact Memory - Pages"
author = "Kai Eckert"
date = "2021-01-19"
kind = "support"
stable = "2021-01-19"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[[links]]
url = "https://github.com/wisslab/judaicalink-generators/blob/master/compact-memory-linking/cm_pages_rdf.ipynb"
label = "Generator script"

[files]
"cm_tagme_pages_data.pickle.gz" = "Page metadata as raw data for Compact Memory, for pages where entity references have been found."
"CM_Seiten_Metadaten.csv.gz" = "Original metadata (pagewise) for Compact Memory."

[[versions]]
version = "2021-01-19"
issued = "2021-01-19"
author = "Marco Rovera"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "cm_tagme_pages_data.pickle.gz"
  bytes = 7323318
  sha256 = "4df9d94b9157e87193967e4b4f2b8ffe3fe7a5ec0a847207e22271b4181a3887"

  [[versions.files]]
  path = "CM_Seiten_Metadaten.csv.gz"
  bytes = 13111336
  sha256 = "7affff32c1da8451ffc536db0cb526d39b09848dfcb59fa70b820493616fcd08"

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the archived version was not regenerated."
+++
Support data for Compact Memory - JL linking (pages).

<!--more-->
