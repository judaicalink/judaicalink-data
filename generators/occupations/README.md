# occupations: generator

The occupations of JudaicaLink as concepts (kind vocabulary): the GND subject headings that `gnd` names as occupations,
with their broader headings, and the occupation IRIs of the older datasets, linked to them. All statements about
occupations are here; the datasets only link to them (decided 2026-10-31).

## History

- 2025-12-16: notebook `occupation_selector.ipynb` (workflow repository).
- 2025-12-18/19: `occupations/scripts/build.py` on Benjamin Schnabel's generator framework (`generator/`), commits
  `cba4b0e` … `0cfd7da`. `original/` has the build script, its documentation and the framework modules it uses.
- 2026-10-31 (Kai Eckert): `generate.py` on the framework, a new design: the data of 2025 was never found, and its
  build made lowercase IRIs (`occupation/rabbiner`) from the literals, which did not describe the IRIs in use
  (`occupation/Rabbiner`).

## Inputs

- `inputs:gnd/lds-2026-02-17`: the complete GND, for the names, broader terms and subject categories of the headings.
- the stable versions of `gnd` (the headings named as occupations) and of records-normalized, bhr, sosy and dbpedia
  (the older occupation IRIs).

## Rules

- GND headings: those `gnd` states as `jl:occupationURI`, the ones the older IRIs are linked to, and all their broader
  headings (general, generic, instantial and partitive broader terms of the GND); `skos:Concept`, the preferred name as
  `skos:prefLabel`, the variant names as `skos:altLabel` (German), `skos:broader`, `gndo:gndSubjectCategory`.
- Older IRIs (`data/occupation/<name>`): `skos:Concept`, the name from the IRI as `skos:prefLabel`, `skos:exactMatch`
  the GND heading. English names (dbpedia-persons) by the table `NAMES` in `generate.py`, chosen by hand: matched by
  name they find false friends (the GND's "Artist" is a circus or variety artiste; its "Rabbi" are the sages of the
  Talmudic period, while bhr and DBpedia mean rabbis of all times: Rabbiner). German names (gnd-persons): the heading
  of that preferred name, else the one heading with that variant name (older spellings: "Lexikograph",
  "Wallfahrer"), preferring headings used as occupations.

## Reproduction

**Reproducible** from the inputs. About two minutes (one pass over the GND dump).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`occupations/scripts/build.py`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/occupations/scripts/build.py) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) |  |
| [`occupations/README.md`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/occupations/README.md) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) | file last changed in `fcff1b5` (2025-12-18) |
| [`occupations/occupations.md`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/occupations/occupations.md) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) |  |
| [`generator/base.py`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/generator/base.py) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) | file last changed in `4ecdef5` (2025-11-27) |
| [`generator/loader.py`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/generator/loader.py) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) | file last changed in `e64b6dd` (2025-12-18) |
| [`generator/metadata.py`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/generator/metadata.py) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) | file last changed in `fa1e8b3` (2025-11-27) |
| [`generator/rdf.py`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/generator/rdf.py) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) | file last changed in `19a1ebd` (2025-11-27) |
| [`generator/util.py`](https://github.com/judaicalink/judaicalink-generators/blob/0cfd7da85d43dfbea6d896baa41173a61b407cb4/generator/util.py) | judaicalink-generators | `0cfd7da` (2025-12-19, bsesic) | file last changed in `f035cf8` (2025-11-27) |
