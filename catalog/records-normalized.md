+++
slug = "records-normalized"
title = "Normalised dates, places and occupations of the records"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["rule-based", "deterministic"]
inputs = ["bhr", "dbpedia-persons", "djh", "epidat", "footprints", "geo-enriched", "gnd-persons", "gnd-persons-entityfacts", "haskala", "hhkeydocs", "hirsch-family", "jre", "nli-records", "sosy", "ubffm-persons", "rujen", "geo-coordinates", "cm-entities"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/records-normalized"
+++

Normalised values next to the free-text values of the record datasets: typed birth and death dates, places and
occupations as IRIs. The original values stay as they are.

<!--more-->

- **Dates** (`records-normalized-dates.ttl.gz`): `jl:birthDateNormalized` and `jl:deathDateNormalized` as `xsd:date`,
  `xsd:gYearMonth` or `xsd:gYear` for the free-text `jl:birthDate` and `jl:deathDate`. Recognised: ISO dates,
  D.M.YYYY, bare years, Hebrew years in letters (converted, marked uncertain), and markers of uncertainty (?, ca., um,
  בערך, …), which set `jl:birthDateUncertain` / `jl:deathDateUncertain`; other values are left out.
- **Places** (`records-normalized-places.ttl.gz`): `jl:birthLocationURI` and `jl:deathLocationURI` for the text values
  of `jl:birthLocation` and `jl:deathLocation`, where a dictionary gives exactly one IRI: pairs of text and IRI
  already in the data, places of cm-entities, places of rujen and geo-coordinates (exact match after lowercasing; for
  "Place, Country" also the part before the comma); records that already have a place IRI are left as they are.
- **Occupations** (`records-normalized-occupations.ttl.gz`): `jl:occupationURI` for text occupations that equal the
  name of an occupation IRI used in the data (case, spaces and underscores normalised), and for every occupation IRI
  that a record states with `jl:occupation` (or the misspelt `jl:occpation` of bhr), whose range is text: one
  property for all occupation IRIs.

The statements are about the records of the datasets named as inputs, never about entity pages.
