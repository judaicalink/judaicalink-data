+++
slug = "ep"
title = "Entity Pages - Judaicalink"
author = "Kai Eckert"
date = "2021-01-22"
example = "http://data.judaicalink.org/data/ep/1000037"
namespaces = ["ep"]
inputs = ["ep-supp"]
stable = "2021-05-28"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[[links]]
url = "https://github.com/wisslab/judaicalink-generators/blob/master/entity-pages/ep_generator.md"
label = "Generator script"

[files]
"entity_pages.ttl.gz" = "Entity Pages RDF data (2098149 triples)."
"ep_labels.ttl.gz" = "preferred and alternative labels for entity pages. See `label_selector.ipynb` in the repository."
"ep_locations.ttl" = "Entity Pages type classification - locations."
"ep_persons.ttl" = "Entity Pages type classification - persons."
"ep_birth_death_date_loc.ttl" = "Birth/death dates and locations for Entity Pages."
"subcategorization.ttl.gz" = "Subcategorization dataset for local Judaicalink resources."

[[versions]]
version = "2021-05-28"
issued = "2021-05-28"
author = "Marco Rovera"
graph = "http://data.judaicalink.org/data/ep"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "entity_pages.ttl.gz"
  bytes = 25813822
  sha256 = "06e4fc3e870e565b4c97db5f4d38ae97cba3c9fc5b15ba81264fda86a42420ea"

  [[versions.files]]
  path = "ep_labels.ttl.gz"
  bytes = 6962357
  sha256 = "44e5dec550100dbd5356033a128e2698488e43bb8cb99cef90be040f97590210"

  [[versions.files]]
  path = "ep_locations.ttl"
  bytes = 183635
  sha256 = "b035b3b2198b7ab304c5ebbf8c8eecda951b263563b295e02116516fa7ade718"

  [[versions.files]]
  path = "ep_persons.ttl"
  bytes = 14948404
  sha256 = "c5c8053f54ab758531eb1be05d0c7da7a7926da9e405bff98550c39c76cf3519"

  [[versions.files]]
  path = "ep_birth_death_date_loc.ttl"
  bytes = 7708440
  sha256 = "e2364f9703a864a9a9c2e80e3550d43ccd93c33aed1f48d0b9e1b2b0af5785e2"

  [[versions.files]]
  path = "subcategorization.ttl.gz"
  bytes = 19243049
  sha256 = "8b1d205a7d5a27ee2605afb8fc0e2d8cbf334ee702b55f48915838b02ec4935c"

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the archived version was not regenerated."

[[changelog]]
date = "2021-03-11"
author = "Marco Rovera"
text = "Birth and death dates and locations added (ep_birth_death_date_loc.ttl)."

[[changelog]]
date = "2021-02-19"
author = "Marco Rovera"
text = "Person and location classification added (ep_persons.ttl, ep_locations.ttl)."

[[changelog]]
date = "2021-02-15"
author = "Marco Rovera"
text = "Preferred and alternative labels added (ep_labels.ttl.gz)."

[[changelog]]
date = "2021-01-22"
author = "Marco Rovera"
text = "First version (entity_pages.ttl.gz)."
+++

Entity Page data for Judaicalink. For further details see the documentation page https://github.com/wisslab/judaicalink-generators/blob/master/entity-pages/readme.md

<!--more-->
