# sosy: generator history

Soundscape Synagoge: persons (cantors and others), by Benjamin Schnabel.

## History

- 2022-06-29 … 2022-07-07: `soundscape-synagoge/generator.py` → `scripts/generator.py`, last change `add17c0`
  ("Datetime converter fixed").
- 2025-11: `sosy/scripts/generator.py` (same code) plus `build.py`.

## Kept version 2022-07-07

**Probable** `add17c0`: the run started 6 minutes after the commit; the code did not change until 2025-11.

## Inputs

Live only: the Soundscape Synagoge API (answers 401 since; a rerun needs access credentials).

## Reproduction

**Not reproducible.** Data issue: `jl:occupation` points to HTML views (`https://data.judaicalink.org/data/html/occupation/Kantor`); fixed in 2026-10-12 (below).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`soundscape-synagoge/scripts/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/add17c080d559b584a0a2b47e08aeca159df8485/soundscape-synagoge/scripts/generator.py) | judaicalink-generators | `add17c0` (2022-07-07, bsesic) |  |

## Framework generator (2026-10-12)

`generate.py` makes a new version from 2022-07-07 (decision 0024; the API cannot be read again). Fix `occupation_iris`
(default on): the 204 addresses of HTML views in `jl:occupation` become the occupation IRIs
`http://data.judaicalink.org/data/occupation/<name>` (all 27 are used by gnd-persons), stated with `jl:occupationURI`;
the 59 occupations given as text stay. With the fix off, the output has the same 1,312 triples as 2022-07-07 (checked).
