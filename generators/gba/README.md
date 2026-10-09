# gba: generator history

Gidal-Bildarchiv (photo archive of the Steinheim-Institut): persons, by Benjamin Schnabel.

## History

- 2022-06-29 … 2022-07-08: `gidal/scripts/generator.py` with the hand-made input `gidal.csv` (from the Gidal BEACON).
- 2024-01-12 output committed; 2025-03-21 `6fce1cd`: `clean_url_string` replaces characters with `_` instead of
  removing them, which **renamed all 24 URIs** (`AlfredKerr` → `Alfred_Kerr`); some prefixes dropped.
- 2025-11: moved to `gba/` with `build.py` on the new generator framework; `gidal.csv` now `gba/source/gidal.csv`.

## Kept version 2025-03-21

**Probable, confirmed by content** `6fce1cd`: the run started 11 minutes after the commit, the URIs follow the new
rule, and the 2025-11 rebuild from the same CSV gives the same triples except the timestamps.

## Inputs

On file: `gidal.csv` (25 lines, unchanged since 2022-07-08).

## Reproduction

**Reproducible** (except `dcterms:created`, which is the run time). The 24 URIs before 2025-03-21 are gone.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`gidal/scripts/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/6fce1cdac61d62f1cbdd710dde5ae2a401a5a05f/gidal/scripts/generator.py) | judaicalink-generators | `6fce1cd` (2025-03-21, bsesic) |  |
