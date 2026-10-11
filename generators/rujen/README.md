# rujen: generator history

Encyclopedia of Russian Jewry (rujen.ru), crawled by Kai Eckert.

## History

- 2014 (Kai Eckert): CoffeeScript crawler and RDF writer (`rujen-to-json.coffee`, `rujen-json-to-rdf.coffee`,
  judaicalink-generators root, 2014-07); the 2014 `rujen.n3` records crawler `84a4b06` and writer `954ac14` (labs VM,
  private backup).
- 2018-10-22: revised Turtle by Maral Dadvar (no code); 2018-11-07 crawler subtree (`kaiec/judaicalink-crawler`
  `47b14ca`).
- 2020-09-28 (Kai Eckert): judaicalink-labs command `generate_rujen.py` (Scrapy crawl + RDF), `1ac14f1`; later moved
  to `legacy/`. 2025-06: a Python rewrite of the CoffeeScript (Benjamin Schnabel), deleted 2025-11.

## Kept version 2020-09-28

**Exact** `1ac14f1`: the generator's self-description (`rujen-metadata.ttl.gz`, written 2020-09-28T06:36:31Z; removed from the version 2026-10-11, 0018) recorded the commit, and running its RDF step on the kept crawl
(`rujen.jsonl.gz`) gives an isomorphic graph (140,472 triples).

## Inputs

On file: `rujen.jsonl.gz` (the crawl) in the kept version. A new crawl of rujen.ru would differ.

## Reproduction

**Reproducible** from the crawl (RDF step; needs the Django/Scrapy setup or a stand-alone port).

## Framework generator

`generate.py` (2026-10-11): the RDF step of `1ac14f1` ported to the framework (stdlib, no change to its logic, including the doubled `/index.php//index.php/` in `jl:describedAt`), input the kept crawl `rujen/2020-09-28/rujen.jsonl.gz`, which it copies into the run. A test run gave exactly the 140,472 triples of the version 2020-09-28 (`jl compare`). The crawl step (Scrapy) is not ported. Not a version.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/data/management/commands/generate_rujen.py`](https://github.com/judaicalink/judaicalink-labs/blob/1ac14f193f827f13a657a7f49dca0c0cf2bd7c25/labs/data/management/commands/generate_rujen.py) | judaicalink-labs | `1ac14f1` (2020-09-28, Kai Eckert) |  |
| [`labs/data/management/commands/_dataset_command.py`](https://github.com/judaicalink/judaicalink-labs/blob/1ac14f193f827f13a657a7f49dca0c0cf2bd7c25/labs/data/management/commands/_dataset_command.py) | judaicalink-labs | `1ac14f1` (2020-09-28, Kai Eckert) | file last changed in `4205d5b` (2020-09-28) |
