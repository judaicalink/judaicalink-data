+++
slug = "cm-tagme"
title = "Linking Compact Memory - Resources and References"
author = "Kai Eckert"
date = "2021-01-19"
namespaces = ["cm-tagme"]
inputs = ["cm-tagme-supp"]
stable = "2021-01-18"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[[links]]
url = "https://github.com/wisslab/judaicalink-generators/blob/master/compact-memory-linking/cm_tagme_resource_reference_rdf.ipynb"
label = "Generator script"

[files]
"cm_tagme_resources.ttl.gz" = "Judaicalink resources (entities) mentioned in Compact Memory (749.446 triples)."
"cm_tagme_references.ttl.gz" = "Description of each single mention (start, end, text, page, confidence scores, 5.246.122 triples)."

[[versions]]
version = "2021-01-18"
issued = "2021-01-18"
author = "Marco Rovera"
graph = "http://data.judaicalink.org/data/cm-tagme"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "cm_tagme_resources.ttl.gz"
  bytes = 3034326
  sha256 = "ae42fdcf74c9b33452dad9110fe6f94aee67cda8a50852812cb448412da56379"

  [[versions.files]]
  path = "cm_tagme_references.ttl.gz"
  bytes = 29040075
  sha256 = "bbf4bb9aab99408eb4e229ac776b4519910411c2e480a0b6ab44694ea7bf4d2e"

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the archived version was not regenerated."
+++

References of Judaicalink resources (entities, mainly persons and places) in Compact Memory.

<!--more-->
