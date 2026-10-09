# compact-memory-supp: generator history

The original page metadata of Compact Memory (UB Frankfurt, Visual Library), as a tab-separated file.

## History

- 2020-06-15: UB Frankfurt's export `CM_Seiten_Metadaten.xlsx` converted to a tab-separated file
  (`excel_to_csv_metadata_frankfurt.ipynb`: `pandas.read_excel` → `to_csv(sep='\t')`), presumably by Marco Rovera
  (not documented).
- 2021-01-19 catalogued as support data of compact-memory. The notebook and the xlsx were added to the workflow
  repository on 2025-12-31 (Benjamin Schnabel, `eee36e7`).

## Kept version 2021-01-19

The file has the same content as `metadata/CM_Seiten_Metadaten.csv.gz` in the workflow repository; its gzip header
dates the CSV to 2020-06-15. It is an input of compact-memory and of the new datasets cm-structure and cm-journals.

## Inputs

The xlsx export of UB Frankfurt (workflow repository `metadata/`, 60 MB; also in the private backup, part 2).

## Reproduction

**Probably reproducible**: re-conversion of the xlsx was not tested byte for byte.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`metadata/excel_to_csv_metadata_frankfurt.ipynb`](https://github.com/judaicalink/workflow/blob/eee36e7baaa00c9016c5a135cdf6c578966a9b40/metadata/excel_to_csv_metadata_frankfurt.ipynb) | workflow | `eee36e7` (2025-12-31, Benjamin Schnabel) | file last changed in `86980c2` (2025-12-31) |
