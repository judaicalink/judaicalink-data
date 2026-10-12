# haskala: generator history

The Library of Haskala (persons from the haskala-library.net database of UB Frankfurt), by Maral Dadvar; regenerated
by Benjamin Schnabel.

## History

- 2019-07-01 (Maral Dadvar, `8f1538a`): `CSV-to-RDF-Haskala.py` (scrapes the person pages), `CSV-to-RDF-Haskalanet.py`,
  `GND-enrich-02.py` (export from a local Fuseki); the README documents manual SPARQL INSERTs against the local GND
  between the steps. A copy with outputs is in `fid-judaica/haskala/` (`965a481`, 2021-06-28).
- 2025-03-24 (Benjamin Schnabel): `f9b8215` (relative paths, endpoint changed to the published SPARQL endpoint),
  `7124d29` (outputs), later the same day `ba26673` (occupation split, `Haskala_net` deleted).
- 2025-11 moved to `legacy/haskala/`.

## Kept versions

- **2019-07-01** (stable): output **exact** (identical to `fid-judaica/haskala/Haskala_enriched.ttl` in `965a481` and to
  the original upload); scripts **probable** `8f1538a` (committed after the upload). It contains all triples of
  `Haskala.ttl`, 288 of the 320 of `Haskala_net`, and 1,871 enrichment triples.
- **2025-03-24**: **exact** (`7124d29` outputs, `f9b8215` scripts). `Haskala.ttl` has exactly the triples of the
  un-enriched `Haskala.ttl` of 2019, so this version is the 2019 state before enrichment, not new data.

## The database (found 2026-10-13)

The Library of Haskala was a Drupal 7 site (haskala-library.net, now offline) on a database of a German-Israeli
research project (2004-2010, Shmuel Feiner, Bar-Ilan University; Zohar Shavit, Tel Aviv University; Christoph Schulte,
University of Potsdam), migrated into Drupal on 2015-04-08/09 (record ids such as `person0001` kept in the migration
maps) and hosted by the Judaica Division of the Frankfurt University Library. The repository
[judaicalink/haskala](https://github.com/judaicalink/haskala) (the new portal by Benjamin Schnabel) holds three dumps
of that database: `research/haskala.sql`, the complete database at its host Pantheon (538 tables, dump completed
2015-04-20, also in `research/Haskala-DB.zip` of 2022); `research/haskala_14_12_2023.sql` (422 tables) and
`Database/haskala_edit_2024-07-12.sql` (400 tables, with CSV and XML exports of each table), reduced copies with the
same content (nodes, field data, taxonomies identical; the CSV exports split multi-line texts and are not usable).
The content was not changed after the migration. The 2019 scrape read the person pages of this site; 2019 and 2025
cover 194 of its 1,980 persons and none of its 525 books.

## Framework generator (2026-10-13)

`generate.py` makes the dataset from the database (decision 0024: made again from the source), true to the database
so that it could be rebuilt from the data without a particular portal (decided 2026-10-13; details in the docstring):

- Input `inputs:haskala/drupal-2015-04-20`: the allow-list of tables of the 2015 dump (`make_input.py`: content,
  schema, migration maps, search configuration; without user accounts, sessions, logs, caches, settings).
  `drupal_sql.py` reads the dump with the standard library.
- All nodes of the seven content types (1,980 persons, 525 books, 327 editions, 1,867 mentions, 667 productions,
  272 prefaces, 19 translations; not the one page of site text), all field values (39,225) and the 809 terms of the
  19 taxonomies. IRIs `data/haskala/<content type>/<node id>`, `data/haskala/<vocabulary>/<term id>`.
- The schema (`haskala-vocabulary.ttl.gz`): classes per content type and properties per field in
  `data/haskala/vocab/`, with the Drupal machine names, types, cardinality, targets, allowed values, and per content
  type the label, help text, order and visibility of each field. The sections of the book page (field groups) and the
  browse and search pages (views) were defined in code, not in the database; they are not in any dump.
- JudaicaLink terms in addition: persons `foaf:Person`, `skos:prefLabel` (German name; for 151 persons without one,
  the part of the title before " - <Hebrew name>"), `skos:altLabel`, `owl:sameAs` VIAF (583), birth and death;
  books `jl:Work`; terms `skos:Concept`, cities `jl:Place` with `geosparql:asWKT`.
- The 2019 IRIs: 194 library persons `dcterms:isReplacedBy` the node of their page (5 of them by two nodes, duplicates
  in the database that 2019 had joined: Alexander, Berlin, Heimann, Jeitteles, Satanow); their GND links (from the
  2019 working list, not in the database) are carried over to the nodes (`haskala-gnd-2019.ttl.gz`). The 32 persons
  of haskala.net (biographies of the University of Potsdam, a different source) keep their IRIs and 2019 triples,
  with their occupations from `Haskala_net.ttl` of 2025-03-24, one value per occupation (`haskala-net.ttl.gz`).

Not done: the duplicates of the database (several nodes for one person) stay as they are; the names, dates and places
of the 2019 GND enrichment are not carried over (they come from the GND, which the entity pages join through
gnd-persons).

## Inputs

`inputs:haskala/drupal-2015-04-20` (the database), and the versions 2019-07-01 and 2025-03-24 (`Haskala_net.ttl`).
Earlier: the source CSVs (`legacy/haskala/sources/`, `legacy/fid-judaica/haskala/sources/`), the website, the GND of
2019 in a local Fuseki.

## Reproduction

From 2026-10-13: **reproducible** from the inputs area. 2019: **not reproducible** (manual updates, local GND), but the
output is on file. 2025: `Haskala_net` is reproducible offline, `Haskala.ttl` needed the website.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`haskala/scripts/CSV-to-RDF-Haskala.py`](https://github.com/judaicalink/judaicalink-generators/blob/8f1538a1f255e49fa329ef8eb9d35c62f7bb37e3/haskala/scripts/CSV-to-RDF-Haskala.py) | judaicalink-generators | `8f1538a` (2019-07-01, Maral Dadvar) |  |
| [`haskala/scripts/CSV-to-RDF-Haskalanet.py`](https://github.com/judaicalink/judaicalink-generators/blob/8f1538a1f255e49fa329ef8eb9d35c62f7bb37e3/haskala/scripts/CSV-to-RDF-Haskalanet.py) | judaicalink-generators | `8f1538a` (2019-07-01, Maral Dadvar) |  |
| [`haskala/scripts/GND-enrich-02.py`](https://github.com/judaicalink/judaicalink-generators/blob/8f1538a1f255e49fa329ef8eb9d35c62f7bb37e3/haskala/scripts/GND-enrich-02.py) | judaicalink-generators | `8f1538a` (2019-07-01, Maral Dadvar) |  |
| [`haskala/scripts/CSV-to-RDF-Haskala.py`](https://github.com/judaicalink/judaicalink-generators/blob/f9b8215519166a50438e3269b3e016a773b5367b/haskala/scripts/CSV-to-RDF-Haskala.py) | judaicalink-generators | `f9b8215` (2025-03-24, bsesic) |  |
| [`haskala/scripts/CSV-to-RDF-Haskalanet.py`](https://github.com/judaicalink/judaicalink-generators/blob/f9b8215519166a50438e3269b3e016a773b5367b/haskala/scripts/CSV-to-RDF-Haskalanet.py) | judaicalink-generators | `f9b8215` (2025-03-24, bsesic) |  |
| [`haskala/scripts/GND-enrich-02.py`](https://github.com/judaicalink/judaicalink-generators/blob/f9b8215519166a50438e3269b3e016a773b5367b/haskala/scripts/GND-enrich-02.py) | judaicalink-generators | `f9b8215` (2025-03-24, bsesic) |  |
