+++
slug = "records-normalized"
title = "Normalised dates, places and occupations of the records"
author = "Kai Eckert"
date = "2026-10-12"
stable = "2026-10-12"
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

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "db9a7f5eac66dcc91f8728aadfe7a5639dc93996"

  [[versions.files]]
  path = "records-normalized-dates.ttl.gz"
  bytes = 1269594
  sha256 = "1454aee91f1a76b72d874f71e0d380705a82dddc90fb309fa70117be7604acf4"
  triples = 189470

  [[versions.files]]
  path = "records-normalized-occupations.ttl.gz"
  bytes = 143092
  sha256 = "a67460dde18b64ff97694b0a26c61f89a192c72c874b239abab2841a7813f622"
  triples = 18961

  [[versions.files]]
  path = "records-normalized-places.ttl.gz"
  bytes = 236874
  sha256 = "afd745bce6ea8bc006a0b2977b208077226e74318bbcf53ada0e010f8aa46993"
  triples = 28213

  [[versions.files]]
  path = "records-normalized-meta.ttl.gz"
  bytes = 3372
  sha256 = "3fb25baeb21fdf62c77a921e2613c27d35021e73ee1a5d1923146348f2c739b4"
  triples = 135

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: normalised dates, places and occupations of the records (dates-normalized, places-linked, occupation-concepts and occupation-fix of kg-complements, decision 0020), for the stable versions; more date forms; all occupation IRIs stated with jl:occupation as jl:occupationURI."
+++

Normalised values next to the free-text values of the record datasets: typed birth and death dates, places and
occupations as IRIs. The original values stay as they are.

<!--more-->

- **Dates** (`records-normalized-dates.ttl.gz`): `jl:birthDateNormalized` and `jl:deathDateNormalized` as `xsd:date`,
  `xsd:gYearMonth` or `xsd:gYear` for the free-text `jl:birthDate` and `jl:deathDate`. Recognised: ISO dates (also
  as dateTimes), year and month (1914-11, 9.1749), D.M.YYYY (also with XX for an unknown day or month), English dates
  (October 28, 1905), bare years from 1 to 2030, years with unknown month and day (1942--) or one of two months
  (1347-06/07), Hebrew years in letters or as numbers (converted, marked uncertain), Hebrew-Gregorian pairs
  (5559-1798), the EDTF value of dates written as Python dictionaries (footprints), and markers of uncertainty (?,
  ca., um, בערך, ~, brackets), which set `jl:birthDateUncertain` / `jl:deathDateUncertain`. Left out: ranges, bounds
  (vor 1593), negative years, and the dates of a record whose one death date is before its one birth date.
- **Places** (`records-normalized-places.ttl.gz`): `jl:birthLocationURI` and `jl:deathLocationURI` for the text values
  of `jl:birthLocation` and `jl:deathLocation`, where a dictionary gives exactly one IRI: pairs of text and IRI
  already in the data, places of cm-entities, places of rujen and geo-coordinates (exact match after lowercasing; for
  "Place, Country" also the part before the comma); records that already have a place IRI are left as they are.
- **Occupations** (`records-normalized-occupations.ttl.gz`): `jl:occupationURI` for text occupations that equal the
  name of an occupation IRI used in the data (case, spaces and underscores normalised), and for every occupation IRI
  that a record states with `jl:occupation`, whose range is text (bhr states its occupation IRIs as `jl:occupationURI` since its version 2026-10-12): one
  property for all occupation IRIs.

The statements are about the records of the datasets named as inputs, never about entity pages.
