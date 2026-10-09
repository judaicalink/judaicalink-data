# djh: generator history

Das Jüdische Hamburg (encyclopedia), crawled by Kai Eckert, revised by Maral Dadvar.

## History

- 2016 (Kai Eckert): crawler `djh-to-json.coffee` (crawl, person detection) and `djh-json-to-rdf.coffee`
  (N3 writer) → `djh.n3`. The code was first committed on 2018-11-07 (`kaiec/judaicalink-crawler` `47b14ca`) and
  taken into judaicalink-generators as `yivo-rujen-djh-macmillan/` (`d0f2e71`), now
  `legacy/yivo-rujen-djh-macmillan/scripts/`.
- 2018-10-22 (Maral Dadvar): `djh.ttl`, a conversion of `djh.n3`; no script found (the prefixes point to an rdflib
  serialisation).
- 2025-06-05: a Python rewrite (`djh_json_to_rdf.py`, Benjamin Schnabel) that was deleted in 2025-11 and never
  produced a dump.

## Kept version 2018-10-22

- The 2016 `djh.n3` (on the labs VM, `/data/archive/data-loading/djh/` and in the old dumps) has the prefix order of
  the CoffeeScript writer, `@de` literals and `foaf:Person`: **probable** output of that script (before its first
  commit).
- The kept 2018 file is the 2016 file with IRIs percent-decoded (non-ASCII characters in IRIs), language tags
  dropped, `jl:describedAt` as a literal, and 11 alternative labels of 4 subjects removed; all its 3,322 triples are in
  the 2016 file. The code of this step is **unknown**.

## Inputs

The 2016 `djh.n3` (labs VM; private backup). The crawl JSON is not on file; the website is the only other source.

## Reproduction

**Partly**: the 2018 transformation can be reconstructed from the 2016 file; the crawl cannot (the crawler stopped
working, by its own README).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`djh-to-json.coffee`](https://github.com/kaiec/judaicalink-crawler/blob/47b14cae871d779645390c729d697163b5db7d5c/djh-to-json.coffee) | judaicalink-crawler | `47b14ca` (2018-11-07, Kai Eckert) |  |
| [`djh-json-to-rdf.coffee`](https://github.com/kaiec/judaicalink-crawler/blob/47b14cae871d779645390c729d697163b5db7d5c/djh-json-to-rdf.coffee) | judaicalink-crawler | `47b14ca` (2018-11-07, Kai Eckert) |  |
| [`crawler.coffee`](https://github.com/kaiec/judaicalink-crawler/blob/47b14cae871d779645390c729d697163b5db7d5c/crawler.coffee) | judaicalink-crawler | `47b14ca` (2018-11-07, Kai Eckert) |  |
| [`package.json`](https://github.com/kaiec/judaicalink-crawler/blob/47b14cae871d779645390c729d697163b5db7d5c/package.json) | judaicalink-crawler | `47b14ca` (2018-11-07, Kai Eckert) |  |
| [`README.md`](https://github.com/kaiec/judaicalink-crawler/blob/47b14cae871d779645390c729d697163b5db7d5c/README.md) | judaicalink-crawler | `47b14ca` (2018-11-07, Kai Eckert) | file last changed in `77cb25c` (2014-06-17) |
