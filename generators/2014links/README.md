# 2014links: generator history

Links from the 2014 versions of yivo and rujen to external datasets (DBpedia agents and places, Freebase,
LinkedGeoData, DM2E, GeoNames, NYTimes), made with the link discovery framework Silk by Dominique Ritze
(2014, catalogued 2017-02-15 by Kai Eckert).

## History

- 2014: Silk runs by Dominique Ritze (link specifications with local paths `C:\Users\domi\…`, `/home/dritze/Judaica/…`).
  The specifications were never in a repository.
- 2017-02-08: the Silk configurations and raw outputs were put on the server (`/data/archive/data-loading/silkruns/`);
  2017-02-15 catalogued.

## Kept version

- **2017-02-15**: the 12 files are byte-identical (decompressed) to the raw Silk outputs in `silkruns/` (2017-02-08).
  Link specifications exist for 8 of them (yivo and rujen × DBpediaAgent, DBpediaPlace, Freebase, LinkedGeoData);
  none for rujenDM2E, yivoDM2E, yivoGeonames, yivoNYtimes. Rule of the existing specs: `skos:Concept`, lower-case
  prefLabel against `rdfs:label`, Jaro-Winkler, threshold 0.1, minimum confidence 0.9.

## Inputs

- Sources: the 2014 graphs of yivo and rujen (on the labs VM, `/data/archive/data-loading/{yivo,rujen}/`).
- Targets: dbpedia.org/sparql (changed since), factforge.net for Freebase (gone), linkedgeodata.org/sparql (largely
  defunct), unknown endpoints for DM2E, GeoNames, NYTimes.

## Reproduction

**Not reproducible**: the target endpoints are gone or changed, 4 of 12 specifications are missing. The yivo
subjects use the mixed-case IRIs of 2014, which yivo 2020 no longer has (0 of 274 match exactly, 266 ignoring
case); the rujen subjects still match (2,283 of 2,284).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| `/data/archive/data-loading/silkruns/Rujen/Config/rujenDBpediaAgentConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Rujen/Config/rujenDBpediaPlaceConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Rujen/Config/rujenFreebaseConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Rujen/Config/rujenLDGOPlaceConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Yivo/Config/yivoDBpediaAgentConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Yivo/Config/yivoDBpediaPlaceConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Yivo/Config/yivoFreebaseConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |
| `/data/archive/data-loading/silkruns/Yivo/Config/yivoLDGOPlaceConfig.xml` | labs VM | – (2017-02-08, Dominique Ritze) | Silk link specification; also in /data/dumps/2014links/current/*/Config/ (identical) |

## Framework generator (2026-10-12)

`generate.py` makes a new version from 2017-02-15 (decision 0024: a systematic error of one dataset is fixed by a new
version; the Silk runs cannot be run again). Fix `drop_person_place_links` (default on): the rujen links were found by
matching names, so rujen persons whose name is a place name (Fanny Berlin, Mikhail Lvov, Paul Marselle, Yakov Lyubin,
…) were linked to places; every link from a record that rujen types as a person to a place is dropped:
`rujenDBpediaPlace` 9, `rujenLGDOPlace` 21, `rujenDM2E` 534 statements (to `data.dm2e.eu/data/place/`), 298 distinct
triples. The other nine files are copied unchanged; with the fix off, the version has the same 5,473 triples as
2017-02-15 (checked). Found with the entity-page closure (decision 0022): the persons were joined with the place
records of Marseille, Berlin, Lviv and Lubin.
