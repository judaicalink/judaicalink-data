# geo-enriched: generator history

Birth and death places of six datasets linked to GeoNames, by Marco Rovera.

## History

- 2019-12-18: catalogued by Marco Rovera. **The generator was not found** in any repository, branch, on the labs VM
  or in Marco Rovera's GitHub repositories.
- 2020-08-03: Kai Eckert added a judaicalink-labs command `geo_enrichment.py` ("not yet working") that looks like a
  port of the original (GeoNames search, first hit, output per dataset and `geo_interlinks.ttl`). It is kept in
  `original/` as the closest available code, **not** as the script that ran.

## Kept version 2019-12-18

**Unknown.** Evidence that the port follows the original logic: the death-place loop tests the raw literal, and the
dump has exactly one result of that quirk (`hirsch/2987`, literal `"NN "` linked to a GeoNames place); the prefixes
match. Unexplained: the haskala file is empty although haskala 2019 has 72 persons with place literals.

## Inputs

The source versions are on file: bhr 2018-10-24, djh 2018-10-22, gnd-persons 2018-11-29, haskala 2019-07-01,
hirsch-family 2018-10-30, ubffm-persons 2019-01-24. External: the GeoNames search API (needs a user name; the
ranking changes).

## Reproduction

**Not reproducible**: original code missing, GeoNames results change, the first hit is taken without
disambiguation.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/enrichment/management/commands/geo_enrichment.py`](https://github.com/judaicalink/judaicalink-labs/blob/f4276a54a4bf89e1eebd1a47f0d1d40d5b3d825b/labs/enrichment/management/commands/geo_enrichment.py) | judaicalink-labs | `f4276a5` (2020-08-03, Kai Eckert) |  |
