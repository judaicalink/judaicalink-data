# 0021 The store is the dumps; inputs that are not published live in an inputs area

Status: accepted · Date: 2026-10-12 · Amends [0018](0018-generator-framework.md) and [0019](0019-dumps-locations-equal.md)

## Context

0019 made the store "the dumps plus everything we keep but do not publish" (full acquisition outputs, private
inputs, …), and 0018 let a version have files kept only in the store (`add-version --store-only`) and named inputs
made outside by checksum, origin and description written into the generator. Porting `compact-memory` (0020)
showed what that would mean: 2 GB of OCR full text in the store next to the published files, and the 1 TB of OCR
XML that made it not covered at all. The published data and the material needed to make it have different
purposes, sizes and lifetimes.

## Decision

- **The store is the dumps.** It holds exactly the files of the catalogued versions, in the layout of a dumps
  location (`<slug>/<version>/<path>`), kept clean and small; every file a version lists is published. The
  framework can always assume a complete local copy of it. There are no files "kept only in the store":
  `add-version --store-only` is gone. "We do not lose data" (0019) is about these files.
- **Inputs that are not published live in the inputs area,** `lokal/inputs/` (`inputs` in `local.toml`): large,
  private or only needed to make datasets (full texts, exports, web caches, files someone sent us). They may not be
  kept forever, or only in a backup.
- **One input = one folder** `<source>/<name>/` (by source, as one input often serves several datasets, e.g.
  `compact-memory/fulltext-2026-10-05-v2/`), with its files in any layout and **one `input.toml`** that describes
  them: `title`, `origin` (a URL where there is one, else text), `description`, `date` (made or received), an
  optional `note`, and a table of the files with size, sha256 and an optional description. One file per input rather
  than one per file: an input of many files (the full-text bundle has 43) shares one origin and description, which
  are edited in one place. `jl add-input` copies or moves files in and writes the file table; the texts are edited
  by hand; `jl check-inputs` checks that every file is described and unchanged.
- **Generators name an input as `inputs:<source>/<name>/`** (all its files) or one file of it. The framework checks
  the files against `input.toml`; the run record names every file by its path in the inputs area and its checksum
  and copies the texts of the input (`input_descriptions`), never a local path. The `-meta` of the version
  describes each such input in one comment (title, description, origin, number and size of the files) and names
  the origin with `prov:used` where it is a URL. This replaces the reference `{sha256, bytes, origin, description}`
  of 0018 (and the `sources` directories searched by checksum).
- **What a version's run used should be in the inputs area,** also when its origin is a public file (one place to
  back up and copy). Inputs too large even for the area (the OCR XML of Compact Memory, about 1 TB) are not inputs
  of a generator; the input made from them is, and its description says how it was made.
- **Losing an input loses no published data:** only the ability to make a dataset again, and what the description
  does not say about the files. The area is backed up and copied as a whole (open issue, with the store).

## Consequences

- Set up 2026-10-12: `inputs/compact-memory/fulltext-2026-10-05-v2` (the full-text bundle, 43 files, 2 GB, moved
  from `lokal/export/`, which keeps a symlink), `inputs/compact-memory/mods-2020-06-15` (the MODS export of UB
  Frankfurt), `inputs/compact-memory/ocr-paths-2026-10-05` (the list of the OCR files),
  `inputs/hirsch-family/csv-2018-10-30` (the CSV of hirsch-family; its generator now reads
  `inputs:hirsch-family/csv-2018-10-30/hirsch_fam_davinci.csv`, same triples). `inputs/README.md` explains the area.
- `compact-memory-supp` gets no new version: its page table stays its file; the other Compact Memory sources are
  inputs.
- The web caches of the lookup datasets (0018: "kept in the store") go into the inputs area when those datasets are
  ported; so do the NLI export and the other inputs of kg-complements (0020).
- Published files of versions stay as they are, including the crawls of rujen, stolpersteine and yivo.
