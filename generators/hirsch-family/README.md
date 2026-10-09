# hirsch-family: generator history

The Hirsch family of Aschaffenburg (from the database "Jüdisches Leben in Unterfranken"), by Maral Dadvar.

## History

- 2018-10-30: `CSV-to-RDF.py` with the input `hirsch_fam_davinci.csv`; committed 2019-08-05 (`40f7c98`).
- 2020-10: an unfinished port to judaicalink-labs by Sara Fischer (branch `scraping`, `generate_hirsch.py`), never
  published.
- 2025-11 moved to `legacy/HirschFamily/`.

## Kept version 2018-10-30

**Exact by re-run** of `40f7c98` on the committed CSV (read as Latin-1, as written on Windows): all 506 kept triples,
plus 7 triples from the CSV header row (`hirsch/IdNr`) that the kept file lacks.

## Inputs

On file: `HirschFamily/input/hirsch_fam_davinci.csv` in judaicalink-generators (now `legacy/HirschFamily/input/`).

## Reproduction

**Reproducible** (the header row must be skipped).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`HirschFamily/scripts/CSV-to-RDF.py`](https://github.com/judaicalink/judaicalink-generators/blob/40f7c98aa2157f9a533c160f80d678643c1509fd/HirschFamily/scripts/CSV-to-RDF.py) | judaicalink-generators | `40f7c98` (2019-08-05, Maral Dadvar) |  |
