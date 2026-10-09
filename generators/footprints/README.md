# footprints: generator history

Footprints: Jewish Books Through Time and Place (Columbia University), by Christian Deuschle; rewritten by
Benjamin Schnabel.

## History

- 2023-12 … 2024-05: `footprints/generator.py` by Christian Deuschle (about 20 commits; places generator merged
  in 2024-03-05). Uses the Footprints API (persons, books, places), lobid GND, VIAF and Google Translate.
- 2025-03-21: Benjamin Schnabel replaced the 594-line generator by a rewrite that keeps only the person loop
  (`e06c88f`, "Footprints generator fixed", ending with the comment "Similar changes can now be applied to book and
  place sections …") and cut it further (`6dd187e`): no sameAs, no dates, `verify=False`. The book and place sections
  were never added back. Presumably the old generator no longer ran (dependencies, an SSL problem); not documented.
- 2025-11: new persons-only `build.py`; the old code moved to `footprints/scripts/archive/`.

## Kept versions

- **2024-03-18** (stable): **exact**, the file is byte-identical to the output committed in `830ad95` (Christian
  Deuschle, 2024-03-18); code as of `173e91b` (2024-03-14). Books with titles, authors, owners, places and dates of
  publication, languages; persons; places.
- **2025-03-21**: **probable** `6dd187e` (its output shape fits only this commit): only `foaf:Person`, `foaf:name`,
  `skos:prefLabel` for 9,974 resources, organisations included.

## Inputs

Live only: `footprints.ctl.columbia.edu/api/` (now behind a bot challenge), lobid GND, VIAF, Google Translate
(unofficial client).

## Reproduction

**Not reproducible**: the API cannot be scripted any more. The kept 2024 file is the only copy of the rich data.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`footprints/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/830ad959e470a6ea45325c96d7d052024077523a/footprints/generator.py) | judaicalink-generators | `830ad95` (2024-03-18, Christian) | file last changed in `173e91b` (2024-03-14) |
| [`footprints/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/6dd187ea72f25e48a633f00772fc05b3c104e9cf/footprints/generator.py) | judaicalink-generators | `6dd187e` (2025-03-21, bsesic) |  |
