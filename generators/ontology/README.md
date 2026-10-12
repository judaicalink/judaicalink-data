# ontology: generator history

The JudaicaLink ontology. The Turtle file is generated from the code blocks of `judaicalink-ontology.md` in the
judaicalink-ontology repository.

## History

- 2018-07: ontology in Markdown (Kai Eckert, moved from judaicalink-loader; update by Maral Dadvar 2018-07-26);
  earlier a PDF of 2017 (labs VM, private backup).
- 2020-09-29: `generate.py` (Kai Eckert, unchanged since): extracts the code blocks of the Markdown into
  `judaicalink-ontology.ttl`.
- Since 2023-04 a GitHub Action regenerates the Turtle file on every change; content by Benjamin Schnabel
  2023–2025 (latest content commit `47f6287`, 2025-11-27).

## Kept version 2025-11-27

**Exact**: the kept file is `judaicalink-ontology.ttl` at `b26c961` (the Action's commit after content commit
`47f6287`); re-running `generate.py` gives the same bytes. It is the ontology served on ontology.judaicalink.org.

## Version 2026-10-12

Imported (`jl import-files`): `judaicalink-ontology.ttl` at `4597e7f`, after pull requests 18, 19 and 20 were merged
(the terms of decision 0020), gzipped; re-running `generate.py` on the Markdown at that commit gives the same bytes.
Made the stable version on 2026-10-12.

## Inputs

`judaicalink-ontology.md` in the judaicalink-ontology repository.

## Reproduction

**Reproducible.**

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`generate.py`](https://github.com/judaicalink/judaicalink-ontology/blob/b26c961b3f5ff018985793134148714f2722c8b4/generate.py) | judaicalink-ontology | `b26c961` (2025-11-27, Benjamin Schnabel) | file last changed in `49159ed` (2020-09-29) |
