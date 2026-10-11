# rujen-translation: generator history

English and German translations of the rujen labels and abstracts (Google Translate), by Kai Eckert.

## History

- 2020-09-28: judaicalink-labs command `generate_rujen_translation.py` (unofficial Google Translate client, with CSV
  caches), last change before the run `39f04c2`; a fix (`af59323`, 2020-09-29) exists only on branch `scraping`.

## Kept version 2020-09-28

**Exact** `39f04c2`: the generator's self-description (`rujen-translation-metadata.ttl`, written 2020-09-28T15:59:16Z; removed from the version 2026-10-11, 0018) recorded the commit; rebuilding from the caches on the kept rujen gives all 15,733
labels and 15,583 abstracts per language. The only differences are 293 broken literals
`"Translated(src=…, text=…)"` (147 en, 146 de) in the kept file, the bug fixed in `af59323`.

## Inputs

The kept rujen 2020-09-28 and the translation caches (four CSV files; not in the dumps since 0015, kept on the labs
VM and in the private backup). Google Translate is external.

## Reproduction

**Reproducible from the caches** (backup); not from scratch (non-deterministic service).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`labs/data/management/commands/generate_rujen_translation.py`](https://github.com/judaicalink/judaicalink-labs/blob/39f04c243cacadc2d12e602a8b1b0929d115413a/labs/data/management/commands/generate_rujen_translation.py) | judaicalink-labs | `39f04c2` (2020-09-28, Kai Eckert) |  |
| [`labs/data/management/commands/_dataset_command.py`](https://github.com/judaicalink/judaicalink-labs/blob/39f04c243cacadc2d12e602a8b1b0929d115413a/labs/data/management/commands/_dataset_command.py) | judaicalink-labs | `39f04c2` (2020-09-28, Kai Eckert) | file last changed in `af44b31` (2020-09-28) |
