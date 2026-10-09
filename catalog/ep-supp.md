+++
slug = "ep-supp"
title = "Entity Pages - Judaicalink"
author = "Kai Eckert"
date = "2021-01-22"
kind = "support"
stable = "2021-03-22"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[[links]]
url = "https://github.com/wisslab/judaicalink-generators/blob/master/entity-pages/ep_generator.md"
label = "Generator script"

[files]
"ep_index.pickle.gz" = "Entity page index."
"ep_inv_index.pickle.gz" = "Entity page inverted index."
"ep_GND_ids.json.gz" = "GND identifiers for Entity Pages."

[[versions]]
version = "2021-03-22"
issued = "2021-03-22"
author = "Marco Rovera"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "ep_index.pickle.gz"
  bytes = 25676352
  sha256 = "4861598f4b6661dbccfe6e4635959e689c4e36881a3803385c5d9d008f73e3f6"

  [[versions.files]]
  path = "ep_inv_index.pickle.gz"
  bytes = 25967633
  sha256 = "5cc60aaa2a9d1bedab608c745edabe281b270f072705e844c0fb6d42c373d22b"

  [[versions.files]]
  path = "ep_GND_ids.json.gz"
  bytes = 266113
  sha256 = "eb4ef014eeda12cfc5cbd8c88a3fc71262e9d8a697695c9304402678a72b1675"

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the archived version was not regenerated."

[[changelog]]
date = "2021-03-15"
author = "Marco Rovera"
text = "GND identifiers of the entity pages added (ep_GND_ids.json)."

[[changelog]]
date = "2021-01-22"
author = "Marco Rovera"
text = "First version (entity page index and inverted index)."
+++

Support data for Entity Pages. For further details see the documentation page https://github.com/wisslab/judaicalink-generators/blob/master/entity-pages/readme.md

<!--more-->
