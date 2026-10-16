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

Fixes (2026-10-15, decision 0024), parameters with the fix as default; with both off the output has the same 140,472
triples as 2020-09-28 (checked):

- `described_at_path`: `jl:describedAt` was `http://rujen.ru/index.php/` + the page path of the crawl, which already
  starts with `/index.php/`, so every page got `/index.php//index.php/<page>` (15,751); now `http://rujen.ru<path>`.
  (Wikidata P10278 uses `https://rujen.ru/index.php?curid=<id>`, the crawl's `id`; not chosen, the page address is
  what the crawl read.)
- `drop_main_page`: the crawl holds the main page of the wiki (`Заглавная_страница`, id 1), which is not an article:
  a `skos:Concept` with an empty abstract, related to the 31 `Служебная:Все_страницы/<letter>` pages, the 2
  categories and `mailto:mail@rujen.ru`, which became records of their own through their `skos:altLabel` (the junk
  subject `<mailto%3Amail%40rujen.ru>`). The main page and these links are left out (70 triples).

With both: 140,402 triples (15,750 records).

Checked, not changed: 18 places have two page addresses in the crawl that differ only in ё/е (`орел`, `орёл`; a
redirect and its target, both crawled with the same `id`); both give the same record IRI, which therefore has two
`jl:describedAt` and two `dcterms:identifier`.

Crawl completeness (checked 2026-10-15, site down since 2026-10, Cloudflare 523): the site's statistics page says
22,243 articles, the crawl has 15,751 pages (ids 1 and 9,907–25,641). The archived list of all pages
(`Служебная:Все_страницы`, Wayback Machine 2026-01-30, first part: АБАЗОВКА … АЛЬТЕРЗОН) has 345 articles, all of them
in the crawl; the 4,741 link targets that were not crawled (e.g. `Петербург`, 972 links) are pages without text
("В настоящий момент текст на данной странице отсутствует", archived 2014). So the crawl looks complete; the
statistics count something else.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/data/management/commands/generate_rujen.py`](https://github.com/judaicalink/judaicalink-labs/blob/1ac14f193f827f13a657a7f49dca0c0cf2bd7c25/labs/data/management/commands/generate_rujen.py) | judaicalink-labs | `1ac14f1` (2020-09-28, Kai Eckert) |  |
| [`labs/data/management/commands/_dataset_command.py`](https://github.com/judaicalink/judaicalink-labs/blob/1ac14f193f827f13a657a7f49dca0c0cf2bd7c25/labs/data/management/commands/_dataset_command.py) | judaicalink-labs | `1ac14f1` (2020-09-28, Kai Eckert) | file last changed in `4205d5b` (2020-09-28) |
