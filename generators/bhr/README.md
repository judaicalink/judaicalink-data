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
