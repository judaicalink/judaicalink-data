# interlinks: generator history

Links between the persons of the JudaicaLink datasets (`owl:sameAs`), by Kai Eckert and Maral Dadvar.

## History

- 2017-02-15 (Kai Eckert): `interlinks.n3`, the yivo–rujen pairs that share a link target in 2014links. No code
  exists; the logic is reconstructed exactly (80 pairs: DBpedia 67, LinkedGeoData 62, DM2E 27 together).
- 2017-10 … 2018-07 (Maral Dadvar): `JudaicaLink-interlink-01 … 04.py` (judaicalink-loader
  `generators/Datasets/Interlinks/`, committed 2018-02-13 `277524a`, with outputs `-02` … `-04-enriched-07`),
  querying a local Fuseki; the steps `-08` and `-09` are in no repository.
- 2018-07-24 moved to judaicalink-generators (`interlinks/`); 2019-05 notebooks by Kai Eckert on name variants
  (later work, not related to the kept version); 2025 path fixes and moves.

## Kept version 2018-07-18

- `interlinks.n3.gz`: logic **exact** (reconstructed from 2014links), original code unknown. Its yivo IRIs (2014)
  do not resolve in yivo 2020 (lower-cased IRIs).
- `interlinks-04-enriched-09.ttl.gz`: **not exact**: it equals the committed `-07` minus 20 triples (a duplicate
  person in bhr) plus 699 preferred labels and 92 `foaf:Person` types; the code of these last steps is missing.

## Inputs

`interlinks.n3`: 2014links (kept). `-09`: Maral Dadvar's local Fuseki (not on file); earlier outputs are in the
repositories.

## Reproduction

`interlinks.n3`: **reproducible** from 2014links. `-enriched-09`: **not reproducible**.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-01.py`](https://github.com/judaicalink/judaicalink-loader/blob/277524ace7c873842f3c827ec0212fc61a459c5d/generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-01.py) | judaicalink-loader | `277524a` (2018-02-13, Maral Dadvar) |  |
| [`generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-02.py`](https://github.com/judaicalink/judaicalink-loader/blob/277524ace7c873842f3c827ec0212fc61a459c5d/generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-02.py) | judaicalink-loader | `277524a` (2018-02-13, Maral Dadvar) |  |
| [`generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-03.py`](https://github.com/judaicalink/judaicalink-loader/blob/277524ace7c873842f3c827ec0212fc61a459c5d/generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-03.py) | judaicalink-loader | `277524a` (2018-02-13, Maral Dadvar) |  |
| [`generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-04.py`](https://github.com/judaicalink/judaicalink-loader/blob/277524ace7c873842f3c827ec0212fc61a459c5d/generators/Datasets/Interlinks/scripts/JudaicaLink-interlink-04.py) | judaicalink-loader | `277524a` (2018-02-13, Maral Dadvar) |  |
