# yivo: generator history

The YIVO Encyclopedia of Jews in Eastern Europe, crawled by Kai Eckert.

## History

- 2014 (Kai Eckert): CoffeeScript crawler and RDF writer (`yivo-to-json.coffee`, `yivo-json-to-rdf.coffee`); the
  2014 `yivo.n3` records crawler `18bd57a` and writer `954ac14` (labs VM, private backup).
- 2018-11-07: crawler subtree (`kaiec/judaicalink-crawler` `47b14ca`, "the crawlers do not work anymore").
- 2020-09-25 … 2020-09-30 (Kai Eckert): judaicalink-labs command `generate_yivo.py` (Scrapy crawl + RDF); the last
  commits (`012c605` "No more IRIs", `79440ed` "FIX: Remove duplicates") are only on branch `scraping`; the master
  copy (moved to `legacy/`) is an older state. 2025-06: a Python rewrite of the CoffeeScript, deleted 2025-11.

## Kept version 2020-09-30

**Exact** `79440ed` (the catalogue named `0a47e95`, a merge commit an hour earlier): the metadata records the
commit, and the RDF step on the kept crawl (`yivo.jsonl.gz`) gives an isomorphic graph (36,019 triples).

## Inputs

On file: `yivo.jsonl.gz` (the crawl) in the kept version.

## Reproduction

**Reproducible** from the crawl. Since 2020 the IRIs are lower-cased, so the yivo links of 2014links and
`interlinks.n3` (2014 IRIs) do not resolve.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/data/management/commands/generate_yivo.py`](https://github.com/judaicalink/judaicalink-labs/blob/79440eddce7afc06ca7075f40ebe79b5bc696025/labs/data/management/commands/generate_yivo.py) | judaicalink-labs | `79440ed` (2020-09-30, Kai Eckert) |  |
| [`labs/data/management/commands/_dataset_command.py`](https://github.com/judaicalink/judaicalink-labs/blob/79440eddce7afc06ca7075f40ebe79b5bc696025/labs/data/management/commands/_dataset_command.py) | judaicalink-labs | `79440ed` (2020-09-30, Kai Eckert) | file last changed in `af44b31` (2020-09-28) |
