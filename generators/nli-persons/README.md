# nli-persons: generator history

Persons from the authority file of the National Library of Israel, by Maral Dadvar. Superseded by nli-records.

## History

- 2019-01 (header 04/01/2019): `NLI-persons-03.py`, committed 2019-08-05 (`724c8ee`) with the input
  `input/auth.json.gz` (`0a40068`, the NLI export "provided by Aaron").
- 2023–2025 (Benjamin Schnabel): truncated test copies of input and output, path changes, a notebook (2024-01-12),
  an empty stub `NLI.py` (2025-06); none of these changed the generator. 2025-11 moved to `legacy/nli-persons/`.

## Kept version 2019-01-25

**Exact by re-run** of `724c8ee` on the committed `auth.json.gz`: 660,752 triples, identical to the kept file.

## Inputs

On file: `legacy/nli-persons/input/auth.json.gz` in judaicalink-generators.

## Reproduction

**Reproducible** (only the change of directory to a local Desktop has to be removed).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`nli-persons/scripts/NLI-persons-03.py`](https://github.com/judaicalink/judaicalink-generators/blob/724c8eeff9b1d53b54060e3a2738c7898ca885bd/nli-persons/scripts/NLI-persons-03.py) | judaicalink-generators | `724c8ee` (2019-08-05, Maral Dadvar) |  |
