+++
slug = "nli-persons"
title = "Persons from NLI"
author = "Kai Eckert"
date = "2019-01-25"
example = "http://data.judaicalink.org/data/nli/Abner_"
namespaces = ["nli"]
stable = "2019-01-25"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/nli-persons"

[files]
"nli-persons.ttl.gz" = "Persons extracted from the authority file of National Library of Israel."

[[versions]]
version = "2019-01-25"
issued = "2019-01-25"
author = "Maral Dadvar"
graph = "http://data.judaicalink.org/data/nli"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "nli-persons.ttl.gz"
  bytes = 4145903
  sha256 = "4483d52aeabd8e2c52a58442db4cfbf6458f0579831653379dd31a7553b0b599"

[[changelog]]
date = "2024-01-12"
author = "Benjamin Schnabel"
text = "A notebook (2024) and a script stub (2025) added to the generator folder (judaicalink-generators); the generator itself and the published version were not changed."
+++

This dataset contains the authors extracted from the authority file of National LIbrary of Israel.

<!--more-->

When available, there is the date of birth and death and list of publications for each author. 
