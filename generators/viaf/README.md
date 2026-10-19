# viaf: generator

The VIAF clusters JudaicaLink uses (decision 0029), made from the yearly VIAF dump.

## History

- 2026-10-19 (Kai Eckert): new dataset.

## Inputs

- `inputs:cascade/2026-10-19`: `viaf-selection.tsv.gz`, the selection of the cascade (`jl cascade` with `lookup.py`).
- `inputs:viaf/clusters-2024-08-04`: the yearly VIAF dump of 2024-08-04, all clusters in RDF as N-Triples
  (`viaf-20240804-clusters-rdf.nt.gz`, 14.7 GB), the only RDF file of the dump. ODC Attribution 1.0.

`lookup.py` gives the cascade VIAF's part: an index of the dump (built once per dump, in `<build>/_index/`, 4.5 GB)
with the cluster numbers and the `schema:sameAs` targets of each cluster (the records of the sources), unescaped as
the generator reads them (VIAF writes `\u` escapes: `Dobříš`).

## Selection

`viaf-selection.tsv.gz`, one row per VIAF number and dataset that links it (`linked`): one of our datasets (any
statement) or another authority dataset (its declared identity, decision 0032), with the current number: the number
itself if the cluster is in the dump, empty if it is not. The dump states no merged or withdrawn clusters, and a
cluster made after the dump is not in it either, so a missing number gets no successor and is not marked deprecated.

## Data

Each selected cluster of the dump is a record `data/viaf/<n>`: `owl:sameAs <https://viaf.org/viaf/<n>>` (the
canonical form); the class of the common layer for `schema:Person`, `schema:Organization`, `schema:Place` and
`schema:CreativeWork`; `skos:prefLabel` the preferred names as VIAF gives them (one per source library, with its
language tag); `skos:altLabel` the `schema:alternateName`; `jl:birthDate` and `jl:deathDate` as given; `owl:sameAs`
the records of the sources VIAF names (`schema:sameAs`: GND, LC, Wikidata, ISNI, BnF, …; canonical forms);
`owl:differentFrom` as given. Left out: IRIs without a path, which name no record (`http://data.bnf.fr/#foaf:Person`),
the source records of the cluster (VIAF's sourceID nodes) and the works of the cluster.

The dump is read in one pass; its lines are not grouped by cluster, so the triples of the selected clusters are
collected in memory. Lines that are not valid N-Triples are left out and listed in the log.

## Version 2026-10-19

213,653 clusters of 231,552 linked numbers (17,899 not in the dump), 2,968,180 triples; 21 lines not valid
N-Triples; 8,461 links without an identifier left out. About six minutes.

## Reproduction

**Reproducible** from the inputs. A newer dump, or a new cascade, is a new input and gives a new version
(`docs/process.md`, 2a).
