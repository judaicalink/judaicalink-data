# compact-memory: generator history

Compact Memory pages (journal, issue, page) on which cm-tagme found a mention, by Marco Rovera.

## History

- 2021-01-18: run; 2021-01-19 committed to judaicalink-generators (`compact-memory-linking/cm_pages_data.ipynb`,
  `cm_pages_rdf.ipynb`, `aefa2e5`). Later life as cm-tagme.

## Kept version 2021-01-18

**Exact**, `aefa2e5`: the committed data logic on the page metadata CSV and the cm-tagme intermediate gives the
intermediate `cm_tagme_pages_data` (747,760 pages), and the RDF logic a file byte-identical to the kept one. The
committed notebooks contain bugs the actual run did not hit (a NameError when saving, a file-name mismatch).

## Inputs

- `CM_Seiten_Metadaten.csv` (= compact-memory-supp, in the dumps).
- `cm_tagme_resource_reference_data` (the cm-tagme intermediate; derivable from the cm-tagme inputs).
- Only pages with a mention are described, so the dataset depends on cm-tagme.

## Reproduction

**Reproducible** from the page metadata and the cm-tagme intermediates (backup).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`compact-memory-linking/cm_pages_data.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/cm_pages_data.ipynb) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`compact-memory-linking/cm_pages_rdf.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/cm_pages_rdf.ipynb) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`compact-memory-linking/README.md`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/README.md) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
