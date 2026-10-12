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

## Framework generator

`generate.py` (2026-10-12, decision 0020): a port of `cm_journals` and `cm_structure` of kg-complements
(`datasets_deterministic.py`, 2026-10-05) without changes to their logic, plus the image link of every page;
`cm_sources.py` holds the functions it needs from `extract_cm_fulltext.py` (cm_indexer of the FID portal). Inputs: the
page table `compact-memory-supp/2021-01-19/CM_Seiten_Metadaten.csv.gz`, and from the inputs area (decision 0021)
`compact-memory/mods-2020-06-15` (MODS records), `compact-memory/ocr-paths-2026-10-05` (the OCR file list, for the page
IRIs) and `compact-memory/fulltext-2026-10-05-v2` (the full-text bundle: which pages are in the index, with date, label
and journal); the version 2021-01-18 for the existing page IRIs. Writes `compact-memory-journals.ttl.gz` (3,707
triples, identical to cm-journals) and `compact-memory-pages.ttl.gz` (4,549,427 triples: cm-structure plus 846,499
image links and the classes). About one minute.

Classes (decided 2026-10-12): journals `schema:Periodical` (as in cm-journals); from the kind in the page table
(`Parent-Type`) `schema:PublicationIssue` (journal issue, 46,620), `schema:PublicationVolume` (journal volume, 593) and
`schema:Article` (article, struct article; 24,463); a node without a kind directly below its journal is a volume
(2,148); pages `jl:Page` (schema.org has no class for a page). Nodes of the other 24 kinds (chapter, correspondence,
title page, …) and the 1,898 nodes without a kind deeper in the hierarchy get no class; the kind stays as
`dcterms:type`. The ontology classes `jl:Journal` and `jl:Issue` are not used (no dataset uses them).

Compared with the version 2021-01-18 (624,682 triples), 4,710 triples are no longer stated (decided 2026-10-12):
the second IRI of 2,060 pages that had two (one per OCR file copy; they are `owl:sameAs` the page that carries the
data, same issue in every case), the 3 pages whose two OCR copies differ (not in the full-text index), the journal
titles as `jl:title` and journal-level image links (now `dcterms:title` from the MODS records and `foaf:page`), and 16
volumes and issues assigned to a second record of the same journal (the page table assigns them to the other).

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`compact-memory-linking/cm_pages_data.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/cm_pages_data.ipynb) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`compact-memory-linking/cm_pages_rdf.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/cm_pages_rdf.ipynb) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`compact-memory-linking/README.md`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/README.md) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
