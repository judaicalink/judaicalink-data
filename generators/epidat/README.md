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
spaCy model `de_core_news_sm`. No snapshot. Since then Epidat's harvesting page names its research data repository
(<https://gitlab.rlp.net/epidat/data>) as the source of all its data; the 2026 generator reads a snapshot of it.

## Reproduction

**Not reproducible.** The catalogue `graph` of the legacy load is `data/epi`, the URIs are `data/epidat/`.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`epidat/scripts/generator.py`](https://github.com/judaicalink/judaicalink-generators/blob/bf6f5e398535d39e18c2c4753349b40eab2cb634/epidat/scripts/generator.py) | judaicalink-generators | `bf6f5e3` (2022-07-27, bsesic) |  |
| [`epidat/README.md`](https://github.com/judaicalink/judaicalink-generators/blob/bf6f5e398535d39e18c2c4753349b40eab2cb634/epidat/README.md) | judaicalink-generators | `bf6f5e3` (2022-07-27, bsesic) | file last changed in `afb6a06` (2022-06-27) |

## Framework generator (2026-10-12)

`generate.py` makes the dataset again from the source, not from 2023-07-14 (decision 0024: the systematic errors are
in the IRIs). Input `inputs:epidat/data-2026-08-13`: the TEI/EpiDoc files of the repository at commit `61046f3`
(one file per gravestone, the same files the 2022 generator read through the older interface) and the cemetery
table (not used yet).

- **IRIs from the Epidat person id** (`data/epidat/hha-2512-1`), one per person. The name IRIs of 2023-07-14
  conflated persons of the same name (2,657 IRIs held 10,432 persons, up to 106) and 236 were clipped; each is stated
  `dcterms:isReplacedBy` the persons named by its `jl:describedAt` links: 26,488 by one person (their entity pages
  stay), 2,615 by several (their entity pages split, 0022), 315 by none (all their persons withdrawn, below).
- **Per person:** the name before the spouse (⚭) and without the civil name in final parentheses as `skos:prefLabel`
  and `foaf:name` (editorial brackets kept as given; 2023 cut names at brackets and `geb.`, giving labels like
  `irsch`), the civil name as `skos:altLabel`; `foaf:gender`; `jl:deathDate` as given; the settlement of the cemetery
  as `jl:deathLocation` with its TGN IRI (GeoNames for five Czech cemeteries) as `jl:deathLocationURI`; `owl:sameAs`
  the GND (77 persons) and Epidat's own person URI `https://lod.academy/epidat/id/<id>` (303 to the Epidat page);
  `jl:describedAt` the Epidat page, as 2023.
- **Left out:** occupations and birth years from the commentaries (2023 found them with spaCy; not standard library),
  the `dcterms:created` time of the run and the RDF-star `jl:hasHebrewDate` of the repair. (The family relations and
  birth dates came later, below.)
- **Source problems:** 63 of 48,041 files are not well-formed XML; 30 (a doubled quote in a link target) are
  repaired, of 8 the person list is parsed alone, 25 have no person list (truncated). 451 persons of 2023 (cemeteries
  `gre`, `kal`, `l10`, `mue`, `nie`, `ora`, `tol`) are not in the repository; Epidat's harvesting interface answers
  "FILE not yet published" for them (except Toledo), so they are not taken over.

Result: 41,378 persons in 268 cemeteries (2023: 37,193 entries in 29,418 IRIs, 222 cemeteries); 416,724 triples.

## Additions (2026-10-15, not a version yet)

Each is a parameter, default on; with all three off the run has the same 416,724 triples as 2026-10-12 (checked).
New input `inputs:epidat/persdata-2026-08-13`: `tsv/epidat_persdata.tsv` of the repository at the same commit
`61046f3` (added there in `2da218f`, 2026-01-28): 10,441 persons with person id, dates of death and birth, name parts,
parents and spouses as names, Gedenkbuch and Yad Vashem numbers, comments. 6,347 of its persons are in the TEI files.

- `birth_dates`: `jl:birthDate` as given, for 3,203 persons (the TEI files have no birth dates), in the forms `YYYY`,
  `YYYY-MM`, `YYYY-MM-DD` and `YYYY/YY`; 19 values in other forms are left out and listed in the log (`1846.05.14`,
  `1800-12-03 oder 1801-12-28`, `Julie`, …). 10 birth dates are after the death date (Dresden, e.g. `dr2-11220-2`);
  records-normalized leaves such pairs out.
- `memorial_links`: `rdfs:seeAlso` the person's entry in the Gedenkbuch of the Bundesarchiv
  (`https://www.bundesarchiv.de/gedenkbuch/de<id>`, the form of Epidat's commentaries; 116) and in the Yad Vashem names
  database (`https://collections.yadvashem.org/en/names/<id>`; 63). Checked: `de627160` is Karl-Heinz Riess, born
  29 October 1907 in Dresden, as `dr2-101082-2`.
- `family_relations`: the relations of the TEI files (`listRelation`, by person id; 10,546 distinct): 6,685
  `schema:parent` (child to parent; direction checked with the patronymics, e.g. `aha-11-1` Kalonymos ben Schlomo →
  `aha-4-1` Schlomo ben Awraham), 5,702 `schema:spouse` and 2,750 `schema:sibling` (both ways). Left out: 394
  relations with a person not in the files, 234 grandparent relations (schema.org has no term). The person table's
  `childOf`/`spouseOf` are names (mostly the patronymic's given name), not used.

Result: 435,243 triples. The person table has 4,094 persons not in the TEI files (wdf 1,111, sul 428, kgh 426,
rmo 364, sbg 329, dr2 198, …): cemeteries or gravestones missing from the repository's TEI folder; not taken over
here (they need their TEI files from the harvesting interface).

Checked 2026-10-15: the harvesting interface now gives TEI files with persons for the first gravestone of `gre`,
`kal`, `mue`, `nie` and `ora` (no person on `l10-1`), so most of the 451 persons of 2023 not taken over are no
longer "not yet published".
