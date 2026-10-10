# stolpersteine: generator history

Stolpersteine in Mainz (from the Wikipedia list), by Maral Dadvar (2018) and Kai Eckert / Patricia Kaluza (2020).

## History

- 2018-11-26 (Maral Dadvar): `Stein-wiki-01.py` (header dated 26/11/2018), committed 2019-07-31 (`22d71f8`); one
  record was fixed by hand (README).
- 2020-09-26 … 2020-10-06: judaicalink-labs command `generate_stolpersteine.py`, started by Patricia Kaluza
  (`63ebdf6`, `22f2ea4`), finished by Kai Eckert (`4a9e253`, "Stolpersteine works"). These commits are only on branch
  `scraping`; the master copy (moved to `legacy/`) does not even parse.

## Kept versions

- **2020-10-06** (stable): **exact** `4a9e253`: the metadata records the commit, and the RDF step on the kept crawl
  (`stolpersteine.jsonl.gz`) gives an isomorphic graph (1,119 triples). 223 persons.
- **2018-11-26**: **probable** `22d71f8` (the only version of the script). 180 persons with 49 scope notes.

## Inputs

2020: the crawl `stolpersteine.jsonl.gz` in the kept version. 2018: the live Wikipedia list of 2018 (not on file;
possibly recoverable from the Wikipedia history, untested).

## Reproduction

2020: **reproducible** from the crawl. 2018: **not reproducible**.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`stolpersteine/scripts/Stein-wiki-01.py`](https://github.com/judaicalink/judaicalink-generators/blob/22d71f829fbe497b802845aaffa80f0484b8311b/stolpersteine/scripts/Stein-wiki-01.py) | judaicalink-generators | `22d71f8` (2019-07-31, Maral Dadvar) |  |
| [`labs/data/management/commands/generate_stolpersteine.py`](https://github.com/judaicalink/judaicalink-labs/blob/4a9e253b35590b5623c2c9212cfcedda8a7e150b/labs/data/management/commands/generate_stolpersteine.py) | judaicalink-labs | `4a9e253` (2020-10-06, Kai Eckert) |  |
| [`labs/data/management/commands/_dataset_command.py`](https://github.com/judaicalink/judaicalink-labs/blob/4a9e253b35590b5623c2c9212cfcedda8a7e150b/labs/data/management/commands/_dataset_command.py) | judaicalink-labs | `4a9e253` (2020-10-06, Kai Eckert) |  |
