# gba: generator history

Gidal-Bildarchiv (photo archive of the Steinheim-Institut): persons, by Benjamin Schnabel.

## History

- 2022-06-29 … 2022-07-08: `gidal/scripts/generator.py` with the hand-made input `gidal.csv` (from the Gidal BEACON).
- 2024-01-12 output committed; 2025-03-21 `6fce1cd`: `clean_url_string` replaces characters with `_` instead of
  removing them, which **renamed all 24 URIs** (`AlfredKerr` → `Alfred_Kerr`); some prefixes dropped.
- 2025-11: moved to `gba/` with `build.py` on the new generator framework; `gidal.csv` now `gba/source/gidal.csv`.
- 2026-10-17 (Kai Eckert): framework generator `generate.py` (below).

## Kept version 2025-03-21

**Probable, confirmed by content** `6fce1cd`: the run started 11 minutes after the commit, the URIs follow the new
rule, and the 2025-11 rebuild from the same CSV gives the same triples except the timestamps.

## Version 2026-10-18

Run of the framework generator (below) with all fixes on: 202 triples.

## Inputs

`inputs:gba/gidal-csv-2022-07-08/gidal.csv`: the hand-made table (header and 24 rows, unchanged since 2022-07-08;
judaicalink-generators `gba/source/gidal.csv` at `dd0d4aa`).

## Framework generator (2026-10-17)

`generate.py`: the logic of `6fce1cd`, reading the CSV with the csv module; the IRIs of 2025-03-21 (from the name by
`clean_url_string`), kept. Fixes (decision 0024), each a parameter with the fix as default:

- `common_terms`: jl:birthDate, jl:deathDate, jl:occupation, jl:hasPublication, jl:hasAbstract and skos:altLabel
  instead of the `gndo:` terms the GND ontology does not have.
- `dates_as_text`: the years as written (text), not xsd:integer.
- `relation_links`: the relation (the name of another person of the table, 10 rows) as gndo:relatedPerson with that
  person's IRI, not as text in `gndo:relation`.
- `whitespace`: names and texts trimmed, inner spaces single (`Max Liebermann `, `Betty  Geb. Van Geldern`).
- `gnd_links`: owl:sameAs the GND entry (10).
- `described_at`: jl:describedAt the archive's page of the entry, found by GND number (10): the target of the
  archive's BEACON, `http://www.steinheim-institut.de/gidal-bildarchiv/query.html?…`, answers 404; the working form is
  `https://www.steinheim-institut.de/gba/query.html?text1=<GND>&kategorie1=GND`.
- `drop_created`: no dcterms:created (the time of the run); when off, taken from the version 2025-03-21.
- `canonical_forms`: IRIs in canonical form (the GND ontology in https).

Run of 2026-10-17: 24 resources (23 persons, 1 organisation), 202 triples, `gba.ttl.gz`. With all fixes off: the same
206 triples as 2025-03-21 (`./jl compare`).

In the table, not changed: some publications are captions of pictures of the person (Eduard Schnitzer, Max
Liebermann), the abstract of Erich Mendelsohn is the caption of a building; "ägyptischen Salon" (for Sudan, twice);
three occupations joined by a comma ("Mathematiker, Professor").

## Reproduction

**Reproducible** (except `dcterms:created`, which is the run time; the framework generator takes it from the version
when `drop_created` is off). The 24 URIs before 2025-03-21 are gone.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`gidal/scripts/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/6fce1cdac61d62f1cbdd710dde5ae2a401a5a05f/gidal/scripts/generator.py) | judaicalink-generators | `6fce1cd` (2025-03-21, bsesic) |  |
