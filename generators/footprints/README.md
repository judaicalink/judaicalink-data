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

- **2026-10-26-2** (stable): as 2026-10-26, with the links of the works to their page on the site.
- **2026-10-26**: from the API (below).
- **2024-03-18**: **exact**, the file is byte-identical to the output committed in `830ad95` (Christian
  Deuschle, 2024-03-18); code as of `173e91b` (2024-03-14). Books with titles, authors, owners, places and dates of
  publication, languages; persons; places.
- **2025-03-21**: **probable** `6dd187e` (its output shape fits only this commit): only `foaf:Person`, `foaf:name`,
  `skos:prefLabel` for 9,974 resources, organisations included.

## Framework generator (2026-10-12)

`generate.py` of commit `0cb49a3` made the version 2026-10-12 from 2024-03-18 with its systematic errors fixed
(decision 0024); every fix is a parameter, default on, and with all of them off the output has the same triples as
2024-03-18. Found in the 2024
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

## From the API (decision 0034)

The API answers again to the framework's User-Agent (0028). `harvest.py` saved every page of every list endpoint
(2026-10-19) and, with `--fill`, the records that other records refer to but the paging missed (until 2026-10-20; the
API throttles, `harvest_driver.py` restarts it every 10 minutes): `inputs:footprints/api-2026-10-20`. `geonames.py`
finds the GeoNames ids of the places (candidates from the GeoNames dump within 30 km, confirmed by the API's
`altname` endpoint): `inputs:footprints/geonames-2026-10-26`. The university network blocks the site since 2026-10
(DNS filter), so these requests run from outside it.

`generate.py` (since 2026-10-25) makes the version from these inputs, true to the API: works, imprints, copies,
footprints, persons, places, actor records, roles and languages with every field, without the editors'
bookkeeping, the rendered descriptions and the narratives; terms in `data/footprints/vocab/`
(`footprints-vocabulary.ttl.gz`); IRIs from the API ids; dates normalised from the API's EDTF (0035, `jl.dates`). The
classes of the persons (person or organisation) are in `record-classes`. The IRIs of 2024 are `dcterms:isReplacedBy`
the records they stood for; the hash of a name stands for all records of that name, so 242 persons and 10 places of
2024 are replaced by several records (the entity pages split them). Version 2026-10-26: 3,765 works, 6,860
imprints, 10,998 copies, 24,482 footprints, 11,642 persons (1,556 with VIAF), 1,027 places (983 with GeoNames; not
confirmed 16, mostly a second record of a place, and 28 without a candidate: regions, countries, misspellings), 24,734
actor records;
replaced: 8,713 persons, 2,185 works, 120 places of 2024 (67 persons, 461 works and 32 places match nothing: names
changed since, and the regions and countries of 2024). The VIAF numbers are below the quality threshold; the ones
judged correct one by one are the linkset ls-footprints-viaf (decision 0037).

## Inputs

API (`footprints.ctl.columbia.edu/api/`) through the harvest above; the versions before 2026-10 also used lobid GND,
VIAF and Google Translate (unofficial client), live.

## Reproduction

The version of 2026-10 is made again from its inputs by `./jl generate footprints`. The versions 2024-03-18 and
2025-03-21 cannot be made again (live services, no saved answers).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`footprints/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/830ad959e470a6ea45325c96d7d052024077523a/footprints/generator.py) | judaicalink-generators | `830ad95` (2024-03-18, Christian) | file last changed in `173e91b` (2024-03-14) |
| [`footprints/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/6dd187ea72f25e48a633f00772fc05b3c104e9cf/footprints/generator.py) | judaicalink-generators | `6dd187e` (2025-03-21, bsesic) |  |
