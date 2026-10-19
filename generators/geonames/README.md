# geonames: generator

The GeoNames features JudaicaLink uses (decision 0029), made from the GeoNames dump. The 801 nodes
`data/geonames/<id>` that geo-enriched 2019-12-18 coined without describing them are records of this dataset.

## History

- 2026-10-16 (Kai Eckert): new dataset (4,419 records).
- 2026-10-19 (Kai Eckert): the selection comes from the cascade of the authority datasets (`jl cascade`,
  decision 0029), with the GeoNames ids of Wikidata; the GeoNames ontology in `https`.

## Inputs

- `inputs:cascade/2026-10-19`: `geonames-selection.tsv.gz`, the selection of the cascade (`jl cascade` with
  `lookup.py`).
- `inputs:geonames/dump-2026-10-15`: `allCountries.zip` (all features), `alternateNamesV2.zip` (alternate names with
  language, Wikipedia links, Wikidata ids), `admin1CodesASCII.txt` (first-level divisions). CC BY 4.0.

`lookup.py` gives the cascade the GeoNames part: an index of the dump (built once per dump, in `<build>/_index/`)
with the feature ids and the Wikidata item of each feature (alternate names of the kind `wkdt`).

## Selection

`geonames-selection.tsv.gz`: one row per GeoNames id and dataset that links it (`linked`): one of our datasets (an IRI
of GeoNames in any form or a record `data/geonames/<id>` as object, `jl.identifiers`) or another authority dataset (its
declared identity, decision 0032), with the current id: the id itself, or empty if the feature is not in the dump.
GeoNames publishes only daily lists of deleted features, no cumulative list of merges or deletions, so no successor is
stated; the ids not in the dump are named in the run log.

## Data

Each record `data/geonames/<id>`: `owl:sameAs <https://sws.geonames.org/<id>/>`, `schema:Place`, `skos:prefLabel` (the
name), `skos:altLabel` (alternate names with their language tag where it is a language; postal codes, IATA/ICAO and
other codes, abbreviations, `fr_1793` and the link rows are left out), `geosparql:asWKT` (`POINT(lon lat)`,
`geosparql:wktLiteral`), `gn:featureClass` and `gn:featureCode` (GeoNames ontology IRIs in `https`, the publisher's
form, e.g. `gn:P.PPLC`), `gn:countryCode`, `gn:population` (if not 0), `gn:parentADM1` (the first-level division, as
GeoNames IRI), `foaf:isPrimaryTopicOf` the Wikipedia articles and `owl:sameAs` the Wikidata item that GeoNames gives.
External IRIs in canonical form; links to JudaicaLink left out (0029).

## Version 2026-10-19

9,100 records of 9,120 linked ids (20 not in the dump), 257,245 triples; linked by wikidata 8,135, gnd 4,067,
geo-enriched 3,054, geo-coordinates 2,600, cm-entities 1,504, records-normalized 513, 2014links 101, epidat 5, lc 1.
8,973 Wikipedia articles, 2,682 Wikidata items. About 15 seconds.

## Reproduction

**Reproducible** from the inputs. A newer dump, or a new cascade, is a new input and gives a new version
(`docs/process.md`, 2a).
