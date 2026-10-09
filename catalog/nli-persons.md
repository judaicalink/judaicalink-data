+++
slug = "nli-persons"
title = "Persons from NLI"
author = "Kai Eckert"
date = "2019-01-25"
example = "http://data.judaicalink.org/data/nli/Abner_"
namespaces = ["nli"]
stable = "2026-09-26"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[files]
"nli-persons.ttl.gz" = "Persons extracted from the authority file of National Library of Israel."

[[versions]]
version = "2026-09-26"
issued = "2019-01-25"
author = "Maral Dadvar"
graph = "http://data.judaicalink.org/data/nli"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "nli-persons.ttl.gz"
  bytes = 4145903
  sha256 = "4483d52aeabd8e2c52a58442db4cfbf6458f0579831653379dd31a7553b0b599"

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++

This dataset contains the authors extracted from the authority file of National LIbrary of Israel.

<!--more-->

When available, there is the date of birth and death and list of publications for each author. 
