# geonames: generator

The GeoNames features JudaicaLink uses (decision 0029), made from the GeoNames dump. New in 2026-10; the 801 nodes
`data/geonames/<id>` that geo-enriched 2019-12-18 coined without describing them become records of this dataset.

## History

- 2026-10-16 (Kai Eckert): new dataset.

## Inputs

- `inputs:geonames/dump-2026-10-15`: `allCountries.zip` (all features), `alternateNamesV2.zip` (alternate names with
  language, Wikipedia links, Wikidata ids), `admin1CodesASCII.txt` (first-level divisions). CC BY 4.0.
- The stable versions of the datasets that link GeoNames (`stable_inputs`, as in gnd), with gnd and geo-enriched as
  their runs of 2026-10-16 and 2026-10-15 until they are versions (`LINKED` in `generate.py`).

## Selection

`geonames-selection.tsv.gz`: one row per GeoNames id and dataset that links it (an IRI of GeoNames in any form or a
record `data/geonames/<id>` as object, `jl.identifiers`), with the current id: the id itself, or empty if the feature
is not in the dump. GeoNames publishes only daily lists of deleted features, no cumulative list of merges or
deletions, so no successor is stated; the ids not in the dump are named in the run log.

## Data

Each record `data/geonames/<id>`: `owl:sameAs <https://sws.geonames.org/<id>/>`, `jl:Place`, `skos:prefLabel` (the
name), `skos:altLabel` (alternate names with their language tag where it is a language; postal codes, IATA/ICAO and
other codes, abbreviations, `fr_1793` and the link rows are left out), `geosparql:asWKT` (`POINT(lon lat)`,
`geosparql:wktLiteral`), `gn:featureClass` and `gn:featureCode` (GeoNames ontology IRIs, e.g. `gn:P.PPLC`),
`gn:countryCode`, `gn:population` (if not 0), `gn:parentADM1` (the first-level division, as GeoNames IRI),
`foaf:isPrimaryTopicOf` the Wikipedia articles and `owl:sameAs` the Wikidata item that GeoNames gives. External IRIs
in canonical form; links to JudaicaLink left out (0029).

## Run of 2026-10-16

4,419 records of 4,431 linked ids, 138,778 triples; linked by gnd 2,765, geo-coordinates 2,600, cm-entities 1,504,
geo-enriched 1,433, records-normalized 513, 2014links 101, epidat 5, nrwbibdjg 1. 4,317 Wikipedia articles, 1,300
Wikidata items. 12 ids are not in the dump (11 linked by geo-coordinates and gnd, e.g. 2813473, 2924574; 1 by
cm-entities). About 45 seconds.

## Reproduction

**Reproducible** from the inputs. A newer dump is a new input and gives a new version.
