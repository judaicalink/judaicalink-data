# nrwbibdjg: generator history

Bibliografie deutsch-jüdische Geschichte Nordrhein-Westfalen (Steinheim-Institut): persons, by Christian Deuschle.

## History

- 2024-05-17 … 2024-05-24: `nrwbibdjg/generator.py` (`c5fca4e`, `68c9692` "generator accelerated"); README
  2024-06-03.
- 2025-11: `nrwbibdjg/scripts/generator.py` (same code) plus `build.py` (Benjamin Schnabel).
- 2026-10-17 (Kai Eckert): framework generator, made from a harvest of the OPAC (below).

## Kept version 2024-05-24

**Exact**: the file is byte-identical to the output committed in `68c9692`.

## Version 2026-10-18

Run of the framework generator on the harvest of 2026-10-17 (counts below).

## Inputs

Of 2024-05-24, live only: the BEACON file and OPAC of the bibliography at the Steinheim-Institut (answered 503 on
2026-10-09), DNB GND records.

Since 2026-10-17:

- `inputs:nrwbibdjg/opac-2026-10-17` (`harvest.py`, one request per second): the BEACON (timestamp 2026-10-13, 806
  GND numbers) and, for each number, the OPAC's list of its titles, unchanged.
- `gnd/2026-10-16`: the class of each GND entry (the source does not say whether a number is a person, a place or an
  organisation).
- `nrwbibdjg/2024-05-24`: the records to replace.

## Reproduction

2024-05-24 is **not reproducible** (live source changed; the 2025-11 output differs). Since 2026-10-17 the dataset is
**reproducible** from the harvest; a new harvest is a new input and gives a new version.

## Data (since 2026-10-17)

Each item of a list has the bibliography's id (a UUID), a COinS, the authors or editors ("(Hg.)"), the title, the rest
of the citation (place and year, or "In: …" with the journal or volume and its id), sometimes a link to an online
resource, and the GND entries involved (authors, editors, subjects) with their names. The COinS has only the first
author and breaks at an "&" in the title, so the list's text is taken. The lists hold the titles linked to a GND
entry (2,250 of the about 7,500 of the bibliography); a search for all titles is not possible.

- Records `data/nrwbibdjg/<GND number>` (the IRIs of 2024-05-24), one per number of the BEACON: the class of the GND
  entry (`foaf:Person`, `foaf:Organization`, `schema:Place`); `foaf:Person` for a number the GND has deleted
  (undifferentiated names); `skos:prefLabel` and `foaf:name` the name the bibliography gives most often;
  `owl:sameAs` the GND; `jl:describedAt` the OPAC's list. No data copied from the GND.
- Works `data/nrwbibdjg/work/<UUID>`, `schema:CreativeWork`: `dcterms:title` ("[Online-Ressource]" taken off),
  `dcterms:issued` (the year of the COinS), `dcterms:creator` / `dcterms:contributor` the names of the authors / editors,
  `gndo:author` / `gndo:editor` the record of a GND entry of the item with that name, `dcterms:subject` the records of
  the other GND entries, `dcterms:bibliographicCitation` the rest of the citation, `dcterms:isPartOf` the journal or
  volume, `rdfs:seeAlso` the online resource, `jl:describedAt` the bibliography's page of the title.
- Journals and volumes `data/nrwbibdjg/work/<id>` (`z…` journals, `_b…` volumes), `schema:CreativeWork`: `dcterms:title`,
  `jl:describedAt` the OPAC's list of their contents.
- 2024-05-24 made work IRIs from the titles (one IRI for equal titles) and took the titles of journals and volumes as
  works too. Each is `dcterms:isReplacedBy` the works or journals and volumes with that title in the lists of its GND
  numbers, failing that the only one with that title; without a successor `owl:deprecated true`.

## Run of 2026-10-17

24,475 triples (2024-05-24: 33,211). 806 records (790 persons, 226 of them with a GND number the GND has deleted; 11
organisations; 5 places), 2,250 works, 365 journals and volumes (33 journals, 332 volumes). Works: 2,253 authors and
162 editors named; 2,107 author, 110 editor and 315 subject links to records; 11 without a title. 2024-05-24 (807
persons, 2,184 works): 806 records keep their IRI; the person `data/nrwbibdjg/` (empty GND number) and 3 works are
deprecated; 2,181 works are replaced, 217 of them by several (equal titles, or a volume that the bibliography gives
one id per contribution, e.g. "Gewalt in der Region": 26).

In the source: one id for two titles (`35ece0f4-…`, the volumes Münster and Detmold of the Historisches Handbuch;
the first in BEACON order is taken); 16 GND numbers with two names (mostly spellings; 121918424 Jütte and Laqueur,
128477008 Engelbrecht and Komorowski); 7777102-3 (Jüdische Gemeinde Reken) is not in `gnd/2026-10-16` and is classed
by its name.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`nrwbibdjg/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/68c96929b12d1e2e22a07a9b81cf03ff90a1dd9e/nrwbibdjg/generator.py) | judaicalink-generators | `68c9692` (2024-05-24, Christian) |  |
