# gnd-persons: generator history

Persons from the GND (rabbis, persons with Israel as area code, the Freimann collection, authors of UB Frankfurt),
with EntityFacts and ZBW links, by Maral Dadvar.

## History

- 2017-04/05 (judaicalink-loader `Persons_GND/`): `person_generator_GND.py` → `_01` (area code XB-IL) and `_02`
  (area code XY), with occupation mapping (`person_generator_GND_Occontology_01/02.py`, `a93751a`, 2017-05-02).
- 2018-02-13: Freimann collection (`Freimann-GND-enrich.py`, loader `85f2bc5`).
- 2018-07-25: authors of UB Frankfurt (`UB-gnd.py`, judaicalink-generators `6d2a287`).
- 2018-10-24: EntityFacts links (`Entityfacts-01.py`, `abe8e67`); 2018-11-29: links to the ZBW Pressemappe
  (`jl-zbw`, no code found).
- 2025-06 path fixes, 2025-11 moved to `legacy/gnd-persons/`.

## Kept version 2018-11-29 (eight files)

| File | Evidence |
|---|---|
| `generated_persons_GND.ttl.gz` | **exact**: the union of the two Occontology outputs in loader `a93751a` (39,622 triples); the merge step is in no script |
| `generated_persons_GND_enriched.ttl.gz` | **unknown**: the file above plus GND enrichment (sameAs, dates, places); no script or output found, the pattern matches `Freimann-GND-enrich.py` |
| `Freimann-GND-enriched-05.ttl.gz` | **exact**: identical to the output in loader `85f2bc5` |
| `ub-authors.ttl.gz` | **exact**: identical to the output in generators `c079830`; script `UB-gnd.py` (`6d2a287`) |
| `Entityfacts-gnd-sameas`, `-freimann-`, `-ubgnd-` | **probable** `abe8e67` |
| `jl-zbw.ttl.gz` | **unknown** (359 links to the ZBW Pressemappe 20. Jahrhundert; no generator found) |

## Inputs

On file: `Freimann-GND-03.rdf`, `tp-records_gnd-ids.csv` (UB Frankfurt), the occupation ontology. Not on file: the
GND of 2017/18 in a local Fuseki (the labs VM has the GND of 2021-03-02, a later state; private backup).

## Reproduction

**Not reproducible**: every person step needs the GND of 2017/18; local paths, Python 2, manual steps between runs.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`generators/Datasets/Persons_GND/scripts/person_generator_GND_01.py`](https://github.com/judaicalink/judaicalink-loader/blob/a93751a6d1ad19ea8c3258ea3701c9114bfab6e0/generators/Datasets/Persons_GND/scripts/person_generator_GND_01.py) | judaicalink-loader | `a93751a` (2017-05-02, Maral Dadvar) |  |
| [`generators/Datasets/Persons_GND/scripts/person_generator_GND_02.py`](https://github.com/judaicalink/judaicalink-loader/blob/a93751a6d1ad19ea8c3258ea3701c9114bfab6e0/generators/Datasets/Persons_GND/scripts/person_generator_GND_02.py) | judaicalink-loader | `a93751a` (2017-05-02, Maral Dadvar) |  |
| [`generators/Datasets/Persons_GND/scripts/person_generator_GND_Occontology_01.py`](https://github.com/judaicalink/judaicalink-loader/blob/a93751a6d1ad19ea8c3258ea3701c9114bfab6e0/generators/Datasets/Persons_GND/scripts/person_generator_GND_Occontology_01.py) | judaicalink-loader | `a93751a` (2017-05-02, Maral Dadvar) |  |
| [`generators/Datasets/Persons_GND/scripts/person_generator_GND_Occontology_02.py`](https://github.com/judaicalink/judaicalink-loader/blob/a93751a6d1ad19ea8c3258ea3701c9114bfab6e0/generators/Datasets/Persons_GND/scripts/person_generator_GND_Occontology_02.py) | judaicalink-loader | `a93751a` (2017-05-02, Maral Dadvar) |  |
| [`generators/Datasets/Persons_GND/scripts/Freimann-GND-enrich.py`](https://github.com/judaicalink/judaicalink-loader/blob/85f2bc5c2bfcf84395c57d24da5f1da6c4d5dd15/generators/Datasets/Persons_GND/scripts/Freimann-GND-enrich.py) | judaicalink-loader | `85f2bc5` (2018-02-13, Maral Dadvar) |  |
| [`gnd-persons/scripts/UB-gnd.py`](https://github.com/judaicalink/judaicalink-generators/blob/6d2a287f5a4aee460e2677c46c7fff0f4b40d769/gnd-persons/scripts/UB-gnd.py) | judaicalink-generators | `6d2a287` (2018-07-25, Maral Dadvar) |  |
| [`gnd-persons/scripts/Entityfacts-01.py`](https://github.com/judaicalink/judaicalink-generators/blob/abe8e67e1114cb00b8ada5b964fbdf828014f2e2/gnd-persons/scripts/Entityfacts-01.py) | judaicalink-generators | `abe8e67` (2018-10-24, Maral Dadvar) |  |
