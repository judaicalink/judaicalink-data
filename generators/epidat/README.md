# epidat: generator history

Epidat, the epigraphic database of the Steinheim-Institut (Jewish gravestones), by Benjamin Schnabel.

## History

- 2022-06-27 … 2022-07-27: `epidat/scripts/generator.py` (judaicalink-generators, 10 commits), scraping Epidat,
  occupations via lobid and spaCy; last functional change `bf6f5e3` (2022-07-27).
- 2023-01-10 output path changed (`1a49b11`); 2025-11-10 the folder was removed ("legacy refactored"), only a README
  remains in `legacy/epidat/`; the code exists only in the history.

## Kept version 2023-07-14

Not a clean generator run: the output of the run of 2022-07-30 (generator **probable** `bf6f5e3`) had broken URIs
(`data/epidat/b'…'`, bytes in an f-string). The kept file is that output repaired outside any repository: the
`b'…'` wrapper was removed apparently by stripping `b`, `B` and `'` from both ends, which also clipped real names
(`Jakob` → `Jako`, `RoslebatLob` → `RoslebatLo`); four subjects were merged, and one RDF-star statement
(`jl:hasHebrewDate`) was added. No code for this repair was found.

## Inputs

Live only: the Epidat harvesting interface of the Steinheim-Institut (answered 503 on 2026-10-09), lobid GND, the
spaCy model `de_core_news_sm`. No snapshot.

## Reproduction

**Not reproducible.** The catalogue `graph` of the legacy load is `data/epi`, the URIs are `data/epidat/`.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`epidat/scripts/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/bf6f5e398535d39e18c2c4753349b40eab2cb634/epidat/scripts/generator.py) | judaicalink-generators | `bf6f5e3` (2022-07-27, bsesic) |  |
| [`epidat/README.md`](https://github.com/judaicalink/judaicalink-generators/blob/bf6f5e398535d39e18c2c4753349b40eab2cb634/epidat/README.md) | judaicalink-generators | `bf6f5e3` (2022-07-27, bsesic) | file last changed in `afb6a06` (2022-06-27) |
