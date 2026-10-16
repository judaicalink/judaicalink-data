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

2019: **not reproducible**: original code missing, GeoNames results change, the first hit is taken without
disambiguation. Since 2026-10-15: **reproducible** (framework generator, below).

## Framework generator (2026-10-15)

`generate.py` makes the dataset again from the source records (decision 0024), offline and deterministically, instead
of transforming 2019: the errors of 2019 come from its method (the first hit of the GeoNames search, without
disambiguation), not from single values. For every `jl:birthLocation` / `jl:deathLocation` text of the stable
versions of bhr, djh, gnd-persons, haskala, hirsch-family and ubffm-persons (19,318 statements, 4,018 distinct texts):

1. a text that is the label of exactly one place of `geo-coordinates` 2026-10-12 (compared as records-normalized
   does) gets that place, `data/geo-coordinates/<name>`, which has its GND and GeoNames links: 2,706 texts;
2. any other text is looked up in the GeoNames dump (`inputs:geonames/dump-2026-10-15`: `allCountries.zip`,
   `alternateNamesV2.zip`) by `gazetteer.py` (rules in its docstring: names and exonyms, qualifiers such as
   "(Rumänien)", "(Landkreis Starnberg)", "(Oberschlesien)", ", Calif.", population and a same-place cluster, ambiguous
   names left out): 844 texts linked, to the `geo-coordinates` place with that GeoNames id where there is exactly one
   (69), else to our record of the GeoNames feature, `data/geonames/<id>` (dataset `geonames`, decision 0029). Nothing
   is copied from GeoNames (CC BY 4.0).
   Left out: 208 ambiguous, 236 without a candidate, 18 whose qualifier fits no candidate ("Prerau (Mähren)",
   "Fürstenstein (Schlesien)"), 5 uncertain ("?"), 1 placeholder.

The JudaicaLink IRIs `data/geonames/<id>` of 2019 (801 nodes with copied GeoNames labels and coordinates, records of
no dataset) are records of the dataset `geonames` since 2026-10-16, so the links keep these objects; the labels and
coordinates of 2019 are not stated here any more. Output: `geo-enriched.ttl.gz`, 17,884 place links (2019: 2,632); 18,585 of the 19,318 statements are linked (bhr 595 of 651,
djh 265 of 307, gnd-persons 16,179 of 16,688, haskala 57 of 70, hirsch-family 24 of 58, ubffm-persons 1,465 of 1,544).
About 25 seconds.

Against 2019, of its 2,632 links: 1,768 the same GeoNames record, 602 the same place as another record (within 30 km,
same country: Jerusalem instead of West Jerusalem, the city instead of its municipality), 173 not linked now (the
record is gone, or the text is left out), 89 another place, which are the errors of 2019: Königsberg was Königsberg in
Bayern (14, now Kaliningrad), Kolin was Köln, Krotoschin was Berlin, Samter was The Villages (Florida), Karlsbad was
Carlsbad (California), Kolberg a mountain in Lesotho, Aurich a hill in Western Sahara, Barmen a village in Namibia,
Pöls was Saint Paul (Minnesota), Austerlitz the Dutch village.

Checks: on the 2,633 `geo-coordinates` labels that have a GeoNames link from the GND, the gazetteer alone gives the
same record for 2,127, the same place for 48, another place for 42 (some of them errors of the GND link: Ostrzeszów
is linked to Golenice, Bad Bramstedt to a place 115 km away) and leaves out 416 (with `RATIO` 5 instead of 10: 2,201,
48, 46, 338). Of 85 random GeoNames matches read by hand, 2 are doubtful (Černovice as Chernivtsi; Neustadt
(Oberschlesien) as a district named Nowe Miasto).

`records-normalized` reads geo-enriched (pairs of text and IRI as its strongest dictionary; records linked here are
skipped there), so it must be made again with the new version, and so must `ep`.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/enrichment/management/commands/geo_enrichment.py`](https://github.com/judaicalink/judaicalink-labs/blob/f4276a54a4bf89e1eebd1a47f0d1d40d5b3d825b/labs/enrichment/management/commands/geo_enrichment.py) | judaicalink-labs | `f4276a5` (2020-08-03, Kai Eckert) |  |
