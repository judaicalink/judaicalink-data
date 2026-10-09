# date-enriched: generator history

Birth and death years parsed from the date literals of several datasets, by Kai Eckert.

## History

- 2020-07-31: judaicalink-labs enrichment command `date_enrichment` (Kai Eckert, `6666a11` framework, `e213873`
  "Parsing of full years": a four-digit `birthDate` becomes `jl:birthYear`, likewise for death).
- 2020-08-03: changes by Sara Fischer (`10caf6e`, `e774691`) and Kai Eckert (`f4276a5`), after the published run.
- Later moved to `labs/data/`, refactored, partly reverted (2021); now `labs/data/management/commands/legacy/`.

## Kept version 2020-07-31

**Exact by content**, `e213873`: there is no metadata, but the rule of this commit recomputes exactly the 88,707
kept triples from the kept versions of bhr, dbpedia-persons, djh, gnd-persons, jre, ubffm-persons, nli-persons
(2019-01-25) and haskala (2019-07-01). The file was written as `date_enriched.ttl` and renamed and gzipped by hand.

## Inputs

All on file: the kept versions of the eight datasets above (the original read every RDF file registered in the labs
database; the list is not recorded, but the content check identifies it).

## Reproduction

**Reproducible.**

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/enrichment/management/commands/date_enrichment.py`](https://github.com/judaicalink/judaicalink-labs/blob/e21387302da9355f2c5f472fae90b0da1cf31dd1/labs/enrichment/management/commands/date_enrichment.py) | judaicalink-labs | `e213873` (2020-07-31, Kai Eckert) |  |
