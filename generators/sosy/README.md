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

**Not reproducible.** Data issue: `jl:occupation` points to HTML views (`https://data.judaicalink.org/data/html/occupation/Kantor`).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`soundscape-synagoge/scripts/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/add17c080d559b584a0a2b47e08aeca159df8485/soundscape-synagoge/scripts/generator.py) | judaicalink-generators | `add17c0` (2022-07-07, bsesic) |  |
