+++
slug = "date-enriched"
title = "Enrichment of Birth- and Deathdates"
author = "Kai Eckert"
authorlink = "http://wiss.iuk.hdm-stuttgart.de/people/kai-eckert"
date = "2020-07-31"
example = "http://data.judaicalink.org/data/bhr/Aach_Löb"
stable = "2026-09-26"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[files]
"date-enriched.ttl.gz" = "Parsed Dates, using Labs Command date_enrichment"

[[versions]]
version = "2026-09-26"
issued = "2020-07-31"
author = "Kai Eckert"
authorlink = "http://wiss.iuk.hdm-stuttgart.de/people/kai-eckert"
graph = "http://data.judaicalink.org/data/date-enriched"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "date-enriched.ttl.gz"
  bytes = 803216
  sha256 = "5d697577d5b4fcf35bdb3b5e504475f46de9c7c45c208a09915620230ad2d9ec"

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++

This is work in progress. The idea is to parse all available dates and create
these additional properties:

- jl:birthYear
- jl:birthMonth
- jl:birthDay

Issues: 

- birthDay might be confused with birthDate. 
- birthDate should be the parsed datetime, current String representation should go to jl:birthDateString.

Same for deathDate, of course.
