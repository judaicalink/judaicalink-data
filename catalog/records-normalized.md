+++
slug = "records-normalized"
title = "Normalised dates, places and occupations of the records"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["rule-based", "deterministic"]
inputs = ["bhr", "dbpedia-persons", "djh", "epidat", "footprints", "geo-enriched", "gnd-persons", "gnd-persons-entityfacts", "haskala", "hhkeydocs", "hirsch-family", "jre", "nli-records", "sosy", "ubffm-persons", "rujen", "geo-coordinates", "cm-entities"]
stable = "2026-10-12"

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
commit = "5194ec7c5788bf0a851f47d1516c44a5d739b7e7"

  [[versions.files]]
  path = "records-normalized-dates.ttl.gz"
  bytes = 1362424
  sha256 = "98781ddfb620791833a70f3ed6bf273dab99067b0bb592c895f81afcd67dcd72"
  triples = 184388

  [[versions.files]]
  path = "records-normalized-occupations.ttl.gz"
  bytes = 166703
  sha256 = "91a5a4e6c050b979b6ff64435e2f8121f96e9c4203e73251084c7bb159e4c2bb"
  triples = 22155

  [[versions.files]]
  path = "records-normalized-places.ttl.gz"
  bytes = 416726
  sha256 = "b557645fad7ceef11f4fb106d3c1b5c08cdb7b797c6fc1d2d5aef3af405e5999"
  triples = 49754

  [[versions.files]]
  path = "records-normalized-meta.ttl.gz"
  bytes = 3150
  sha256 = "3ebd7e65e374ae22d2a6db64113becff2e1a5a3d55f31a24b8d67afae0d5cabc"
  triples = 135

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "First version: normalised dates, places and occupations of the records (dates-normalized, places-linked, occupation-concepts and occupation-fix of kg-complements, decision 0020), for the stable versions; all occupation IRIs as jl:occupationURI."
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
