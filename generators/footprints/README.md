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

## Framework generator (2026-10-12)

`generate.py` makes a new version from 2024-03-18 with its systematic errors fixed (decision 0024); every fix is a
parameter, default on, and with all of them off the output has the same triples as 2024-03-18. Found in the 2024
file and its generator (`830ad95`):

- `owl:sameAs` as text, never as IRIs (2,971; 673 of them "None", where the VIAF record had no GND number): the
  entity pages ignored them, so Footprints persons were not joined with the GND, VIAF and NLI records;
- the relations of the books (author, publisher, printer, editor, …) as text holding footprints IRIs (6,029), and
  `gndo:ditor` for `gndo:editor` (86);
- the book loop wrote the dates of its persons as the text of a Python dictionary, the birth date as
  `jl:deathDate`; 220 of the 222 repeat a value of the person loop, the other two (one person) become EDTF values;
- the resource of the empty name (the hash of `""`): the authors and publishers without a name, 74 links;
- `dcterms:created`, the time of the 2024 run for each resource (11,571);
- empty abstracts (706), "None" as `jl:describedAt` (260) and `gndo:associatedPlace` (1), two addresses with a
  doubled prefix;
- `geosparql:asWKT` with a stray leading quote and "+-" for negative numbers (99).

Not changed: the GND numbers of places (`gndo:gndIdentifier`, 139) are the first hit of a name search in lobid and
may be wrong; `jl:describedAt` keeps the VIAF and GND pages of the book loop, which repeat `owl:sameAs`.
The 2025 persons (1,296 names not in 2024, no Footprints ids) are not taken over.

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
