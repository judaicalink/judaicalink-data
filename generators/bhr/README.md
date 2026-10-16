# bhr: generator history

Biographisches Handbuch der Rabbiner (Steinheim-Institut), by Maral Dadvar.

## History

- Round 1 (2017-09-14 … 2017-10-09, judaicalink-loader `generators/Datasets/BHR/Round1/`): crawl of the BHR website
  (`Scrapping_Persons_01.py`), content extraction, RDF conversion, matching against the GND and JudaicaLink in a
  local Fuseki (`BHR-GND.py`, `BHR-vs-GND-01.py`, `BHR-vs-JudaicaLink-01.py`).
- Round 2 (2018-05-03, loader `5a51e8c`): re-crawl (`Scrapping_Persons_03.py`) and integration of new and old
  data (`Integrate-new-old-02/03/04.py`, outputs `bhr-final` … `bhr-final-05`).
- 2018-07-24 moved to judaicalink-generators (`bhr/`) by Kai Eckert; 2018-10-24 EntityFacts links
  (`Entityfacts-01.py`, Maral Dadvar).
- Later: README 2019-07-31; 2025-06 path fixes and Python-3 reformatting (Benjamin Schnabel, no functional
  change); 2025-11 moved to `legacy/bhr/`.
- 2026-10-12: framework generator transforming 2018-10-24 (fixes; below, superseded).
- 2026-10-16 (Kai Eckert): made from a full harvest of the Biographisches Portal der Rabbiner (below).

## Kept version 2018-10-24

- `bhr-final-05.ttl.gz` (2018-05-03): **exact**, byte-identical to the output committed in loader `5a51e8c`;
  re-running `Integrate-new-old-04.py` on the committed inputs gives the same 31,034 triples.
- `Entityfacts-bhr-sameas.ttl.gz` (2018-10-24): **probable** `Entityfacts-01.py` at generators `abe8e67`, run with
  the bhr lines active (the committed state writes the ub-gnd file). 663 persons.

## Inputs

- On file (in the repositories): the Round 1 sources (CSVs) and all intermediates incl. `bhr-new-enrich.rdf` and
  `bhr-final-02 … -05`; missing: `new1-cleaned.csv`.
- External: the BHR website (crawled 2017/2018, changed since), the GND and JudaicaLink in a local Fuseki (not on
  file), EntityFacts (live).

## Reproduction

The final integration step is **reproducible** from the committed intermediates. The chain before it and the
EntityFacts links are **not**: local paths (`C:\Users\Maral\Desktop`), Python 2, the local GND of 2017, a changed
website, changed EntityFacts answers.

Since 2026-10-16 the dataset is **reproducible** from the harvest of the portal (`inputs:bhr/portal-2026-10-16`);
a new harvest is a new input and gives a new version.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`generators/Datasets/BHR/Round1/scripts/Scrapping_Persons_01.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/Scrapping_Persons_01.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round1/scripts/ContentExtraction.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/ContentExtraction.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round1/scripts/Encyc-to-RDF.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/Encyc-to-RDF.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round1/scripts/Encyc-to-RDF-ID.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/Encyc-to-RDF-ID.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round1/scripts/BHR-GND.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/BHR-GND.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round1/scripts/BHR-vs-GND-01.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/BHR-vs-GND-01.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round1/scripts/BHR-vs-JudaicaLink-01.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round1/scripts/BHR-vs-JudaicaLink-01.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round2/scripts/Scrapping_Persons_03.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round2/scripts/Scrapping_Persons_03.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round2/scripts/Integrate-new-old-02.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round2/scripts/Integrate-new-old-02.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round2/scripts/Integrate-new-old-03.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round2/scripts/Integrate-new-old-03.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`generators/Datasets/BHR/Round2/scripts/Integrate-new-old-04.py`](https://github.com/judaicalink/judaicalink-loader/blob/5a51e8c8f87613481b5bc9627738d9c3326f8b6a/generators/Datasets/BHR/Round2/scripts/Integrate-new-old-04.py) | judaicalink-loader | `5a51e8c` (2018-05-03, Maral Dadvar) |  |
| [`bhr/Round2/scripts/Entityfacts-01.py`](https://github.com/judaicalink/judaicalink-generators/blob/abe8e67e1114cb00b8ada5b964fbdf828014f2e2/bhr/Round2/scripts/Entityfacts-01.py) | judaicalink-generators | `abe8e67` (2018-10-24, Maral Dadvar) |  |

## Framework generator of 2026-10-12 (superseded)

Until 2026-10-16, `generate.py` made a new version from 2018-10-24 (decision 0024: a systematic error in one dataset is fixed by a new
version of it; the chain above cannot be run again, so the previous version is transformed). The fixes are
parameters, on by default; with all of them off the output has the same 32,884 triples as 2018-10-24 (checked):

| Parameter | Fix | Triples |
|---|---|---|
| `drop_service_page` | `owl:sameAs` the DNB EntityFacts service page, stated for every person with a GND number | 783 removed |
| `drop_empty` | links with an empty identifier (`d-nb.info/gnd//`, `hub.culturegraph.org/entityfacts//`, the Steinheim GND query `text1=/`), empty literals, the GND number placeholder `"NA"` | 9 + 2,141 + 1,692 removed |
| `split_mixed` | Glückmann (BHR id 572) and Gunzenhausen (638) held the entries, abstracts and publications of themselves and Gutheim (640), grouped by their empty GND number in the integration of 2018; each keeps its own (the record's death date matches one abstract each, the BHR page order 372 < 398 < 399 is alphabetical, Gutheim's record holds only his own) | 15 removed |
| `occupation_uri` | `jl:occpation` (typo) with occupation IRIs → `jl:occupationURI` | 2,900 changed |
| `portal_links` | `owl:sameAs` the page of the BHR database of 2018 (`http://steinheim-institut.de:50580/cgi-bin/bhr?id=N`, no longer answering; a page is not the person) → `jl:describedAt` the page of the same id in the Biographisches Portal der Rabbiner, `https://www.steinheim-institut.de/cgi-bin/bhr?id=N` (added 2026-10-15) | 2,535 changed |
| `portal_gnd` | the GND numbers of the portal's BEACON as `owl:sameAs <http://d-nb.info/gnd/…>` for records of that BHR id without a GND link (added 2026-10-15) | 1 added |

The portal (2026-10-15) uses the ids of 2018: the page of every id names the person of our record with that id
(checked for all 781 records reached through the BEACON and for 12 records without GND number, fetched by id). The
portal's own links and Wikidata (P10405) write the id without leading zeros; the page shows it zero-padded. Input
`inputs:bhr/portal-2026-10-15` (`fetch_portal.py`): the BEACON (timestamp 2025-06-05, 805 GND numbers) and, for each
number, the page it leads to with its BHR id. Of the 805: 778 our records have already, 25 belong to ids that are not
in the 2018 data, one to id 71, held by two records (Auerbach Hirsch and Auerbach Benjamin-Hirsch, left out), one is
new (Lazarus, Arnold); none contradicts a GND number of ours. The literal `jl:describedAt` "BHR I.1, 121, id:1"
(volume, page and id of the printed handbook) is kept.

In 2021 the empty GND links joined the three persons into one legacy entity page (`ep/1012090`), and the service
page would join the 783 persons into one group when every `owl:sameAs` target is a key (decision 0022).

## Generator from the portal (2026-10-16)

`generate.py` makes bhr from the Biographisches Portal der Rabbiner, true to the portal (decision 0026, as haskala
and hhkeydocs); the transform of 2018-10-24 above is replaced (it is in the git history).

**Input** `inputs:bhr/portal-2026-10-16` (`harvest_portal.py`): the pages of all 2,703 entries (ids 1 … 2703; the
numbers above answer "Eintrag nicht vorhanden") and the BEACON (timestamp 2025-06-05, 805 GND numbers).

**The pages:** a heading (the name with variants, e.g. "AACH, Löb (hebr. Juda-L.)", "EGER, Moses, bürgerlich Moses
SCHLESINGER"; no Hebrew script), the reference to the printed handbook ("BHR I.1, 121"; BHR I and II), a list with
"Geb." (1,911), "Gest." (2,063) and the biography, and up to seven sections of texts: Literatur (2,553 entries have
it), Dokumente (1,594), Publikationen (1,396), Dissertation (624), Bildmaterialien (542), Epigraphik (522),
Manuskripte (345). The box "Externe Quellen" shows the GND number of the entry (805 entries, exactly the numbers of
the BEACON, one page each) and links the portal looks up in DNB EntityFacts (VIAF, LC, Wikidata, Wikipedia, …), which
are not the portal's own statements and are not taken over (decision 0029).

**The model** (three files):

| File | Content |
|---|---|
| `bhr.ttl.gz` | one record per entry, `data/bhr/<id>` (the id without leading zeros, as the portal's links and Wikidata P10405 write it), `foaf:Person`: `rdfs:label` the heading as given; `skos:prefLabel` the name (the first two parts of the heading, "SURNAME, given names", the surname written as a name: "Aach, Löb"); `skos:altLabel` the names introduced by auch, bürgerlich, gen., genannt, eigentlich, früher, vormals, verh. (titles, abbreviated Hebrew forms and remarks stay in the heading); `jl:birthDate`/`jl:birthLocation` and `jl:deathDate`/`jl:deathLocation` as the page gives them ("ca. 1750", "Trier"; records-normalized normalises them); `jl:hasAbstract` the biography (the other items of the list, one per line); `dcterms:bibliographicCitation` the handbook reference; `jl:describedAt` the page; `jl:occupationURI` `data/occupation/Rabbi` (parameter `rabbi`, as in 2018: derived from the scope of the handbook, a handbook of rabbis; the pages do not state it); the texts of the sections with the properties of `data/bhr/vocab/` (dissertation, document, manuscript, publication, image, epigraphy, literature), the publications and dissertations also as `jl:hasPublication` |
| `bhr-beacon.ttl.gz` | the portal's BEACON: the record `owl:sameAs <https://d-nb.info/gnd/<n>>`, 805 links (the user's decision: the Steinheim-Institut publishes it, so it is a file of its own) |
| `bhr-vocabulary.ttl.gz` | the seven section properties (labels de/en, domain, range) |

**Replacements of the records of 2026-10-12** (name IRIs such as `data/bhr/Aach_Löb`): `dcterms:isReplacedBy` the
record of the BHR id in their `jl:describedAt` ("…, id:<n>"; 2,532 records; 3 that held two entries in 2018,
Auerbach_Hirsch 71/74, Pollak_Markus 1412/1413, Rappaport_Isaak 1448/1449, by both). The 368 records of 2018 without
an id came from another list (with name and at most life years; 258 repeat the name of a record with an id, as
`…-1`); they are replaced by the record with the same name (case and spaces ignored) if exactly one has it and no
year contradicts: 241; 117 have no record of that name (other spellings, e.g. "Altmann, Alexander" for "ALTMANN,
Alexander Israel, Prof. Dr.", "Brüll, Nehemia" for "BRÜLL, Nehemiah, Dr.") and 10 several. These 127 are
`owl:deprecated true` (decided 2026-10-16): the old IRIs made from names could not always be matched; whoever has one
on file looks up the entry in the portal and links its new IRI. They are named in the run log.

**Against 2026-10-12:** all 780 GND links of 2018 are in the BEACON file, identical. Not taken over: the links that
the 2018 integration looked up in EntityFacts (`Entityfacts-bhr-sameas.ttl.gz`: VIAF 661, ISNI 335, Wikidata 276, LC
254, DDB, Wikipedia, Kalliope …), which by decision 0029 come through the authority datasets and linksets, and the
years the 2018 integration extracted from the dates (the full texts are given instead).

**Run of 2026-10-16:** 2,703 records, 80,648 triples in `bhr.ttl.gz`, 805 in `bhr-beacon.ttl.gz`, 42 in the
vocabulary; about one second.
