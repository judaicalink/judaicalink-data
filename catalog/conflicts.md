+++
slug = "conflicts"
title = "Conflicting statements of the records of one person"
author = "Kai Eckert"
date = "2026-11-10"
kind = "complement"
method = ["rule-based", "deterministic"]
namespaces = ["conflicts"]
inputs = ["ep", "records-normalized", "bhr", "dbpedia", "djh", "epidat", "footprints", "gba", "geo-coordinates", "geonames", "gnd", "haskala", "hhkeydocs", "hirsch-family", "jre", "lc", "nli-records", "nrwbibdjg", "rujen", "sosy", "stolpersteine", "ubffm-persons", "viaf", "wikidata", "yivo"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/conflicts"
+++

Where the records of one person, brought together on an entity page, state different years or places of birth or
death. One quality annotation (`dqv:QualityAnnotation`, `oa:Annotation`, `dcterms:type "conflict"`) per person and
property: `jl:onProperty` names the property (`jl:birthDate`, `jl:deathDate`, `jl:birthLocationURI`,
`jl:deathLocationURI`), `oa:hasTarget` the records that state a value, `oa:bodyValue` the values per record.

Years conflict when they are more than a year apart (a year apart comes from calendar conversions); dates the source
marks as uncertain are left out. Places conflict when they are more than 25 km apart and both are settlements; a
country or region against a place in it is no conflict. Compared are the facts the sources state; place links
derived from the text of a place are not.

The annotations are about records, never about entity pages.
