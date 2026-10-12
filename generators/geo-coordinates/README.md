# geo-coordinates: generator history

Coordinates of the birth and death places named in the JudaicaLink datasets, from the GND, by Maral Dadvar.

## History

- 2018-07/08: `Location-coor-02-02.py` (→ `city-geocoor-04-all.ttl`) and `Locaion-coor-03.py` (→ `city-geocoor-05/06/07`),
  committed 2018-08-08 (`b21f1dd`); README 2018-08-09.
- 2025-06 path fixes, 2025-11 moved to `legacy/geocoordinates/`.

## Kept version 2018-08-08

**Probable** `b21f1dd`: the file is dated 21 minutes before the commit; no output in the repository.

## Inputs

The birth and death places of all datasets and the GND, both in a local Fuseki of 2018 (not on file); the
intermediate `city-geocoor-04-all.ttl` is missing.

## Reproduction

**Not reproducible.** The places get URIs without a namespace (`data/Aachen`), see `docs/open-issues.md`.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`geocoordinates/scripts/Location-coor-02-02.py`](https://github.com/judaicalink/judaicalink-generators/blob/b21f1dd963759f20ac0ed7bb5c56e457cf3f19b8/geocoordinates/scripts/Location-coor-02-02.py) | judaicalink-generators | `b21f1dd` (2018-08-08, Maral Dadvar) |  |
| [`geocoordinates/scripts/Locaion-coor-03.py`](https://github.com/judaicalink/judaicalink-generators/blob/b21f1dd963759f20ac0ed7bb5c56e457cf3f19b8/geocoordinates/scripts/Locaion-coor-03.py) | judaicalink-generators | `b21f1dd` (2018-08-08, Maral Dadvar) |  |

## Framework generator (2026-10-12)

`generate.py` makes a new version from 2018-08-08 (decision 0024; the lookups cannot be run again). Fixes, as
parameters with the fix as default:

- `namespace_iris`: the 2,701 places get `data/geo-coordinates/<the same name>` instead of `data/<name>`; each old
  IRI is stated `dcterms:isReplacedBy` its new IRI, so the entity pages keep their IRIs and the links of other
  datasets to the old IRIs (`dbp-wiki-geo-linking`: 2,150; `corrections-links`: 4 deletions) stay valid through the
  replacement (0022); `records-normalized` uses the new IRIs when it is made again.
- `place_type`: `jl:Place` instead of `skos:Concept`.
- `drop_lat_lon`: the `jl:lat`/`jl:lon` of Glogau, Naugard and Rheydt have the values swapped and repeat their
  `geo:asWKT`; dropped.

With the fixes off, the output has the same 18,674 triples as 2018-08-08 (checked). With them: 21,369 triples in
`geo-coordinates.ttl.gz`.
