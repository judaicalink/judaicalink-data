# occupations: generator history

Occupations as concepts, linked from the occupation literals of the graph, by Benjamin Schnabel (2025-12, for the
FID portal). The catalogue has no version: no dump of it is known.

## History

- 2025-12-16: notebook `occupation_selector.ipynb` (workflow repository).
- 2025-12-18/19: `occupations/scripts/build.py` on Benjamin Schnabel's generator framework (`generator/`), commits
  `cba4b0e` … `0cfd7da`. `original/` has the build script, its documentation and the framework modules it uses.

## Inputs

The union graph of a JudaicaLink SPARQL endpoint (all `jl:occupation` literals), the entity-page graph, DBpedia and
GND SPARQL.

## Reproduction

**Partly**: needs the whole graph loaded in an endpoint and the external endpoints. The URIs are coined under
`data/occupation/`, while the catalogue entry says `namespaces = ["occupations"]` (to be corrected).

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
