+++
slug = "ubffm-persons"
title = "Persons from ubffm"
author = "Kai Eckert"
date = "2019-01-25"
example = "http://data.judaicalink.org/data/ubffm/Aaron_Emmerich_Gumpertz"
namespaces = ["ubffm"]
stable = "2026-09-26"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[files]
"ubffm-authors.ttl.gz" = "Persons extracted from Judaica collection of University Library of Frankfurt. Names are both in transcription and Hebrew"
"ubffm-authors-02.ttl.gz" = "Persons extracted from Judaica collection of University Library of Frankfurt. Names are only in transciption"

[[versions]]
version = "2026-09-26"
issued = "2019-01-25"
author = "Maral Dadvar"
authorlink = "http://wiss.iuk.hdm-stuttgart.de/people/maral-dadvar"
graph = "http://data.judaicalink.org/data/ubffm"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "ubffm-authors.ttl.gz"
  bytes = 505187
  sha256 = "6cc3ae3df6bb6972230cb77c87a269cc9cffd0d63047f62164a77ba3771f0364"

  [[versions.files]]
  path = "ubffm-authors-02.ttl.gz"
  bytes = 408010
  sha256 = "a6ab1fe57f453fe962fdc0066cca216207a55e0f45d35d7ad0eb526b3cce50e2"

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++

This first dataset contains authors names from Judaica collection of University Library of Frankfurt.

<!--more-->

Moreover, the authors for whom a GND-ID was available, were further enriched with their personal information extracted from GND.
