+++
slug = "date-enriched"
title = "Enrichment of Birth- and Deathdates"
author = "Kai Eckert"
date = "2020-07-31"
example = "http://data.judaicalink.org/data/bhr/Aach_Löb"
stable = "2020-07-31"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[files]
"date-enriched.ttl.gz" = "Parsed Dates, using Labs Command date_enrichment"

[[versions]]
version = "2020-07-31"
issued = "2020-07-31"
author = "Kai Eckert"
graph = "http://data.judaicalink.org/data/date-enriched"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "date-enriched.ttl.gz"
  bytes = 803216
  sha256 = "5d697577d5b4fcf35bdb3b5e504475f46de9c7c45c208a09915620230ad2d9ec"

[[changelog]]
date = "2020-08-03"
author = "Sara Fischer"
text = "Date parsing of the generator (judaicalink-labs, date_enrichment) extended; the archived version was not regenerated."
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
