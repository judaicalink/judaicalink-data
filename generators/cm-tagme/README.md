# cm-tagme: generator history

Mentions of JudaicaLink entities in the Compact Memory full text, found with the entity linker TagMe, by Marco Rovera.

## History

- 2020: TagMe annotation of the Compact Memory OCR text in Marco Rovera's working folder
  (`tagme_linker.ipynb`: TagMe REST API, lang=de, epsilon 0.05, pre-filter 0.25/0.25, language filter per page;
  `tagme2pickle.ipynb`: 16,426,597 mentions into `cm_entities_tagme.pickle`). These steps were never in the
  generators repository; the working folders are on the labs VM (`/data/cm/scripts/cm`) and copied into the
  workflow repository (`legacy/scripts/cm/`, 2025-12-16).
- 2021-01-18: run of the data and RDF step; 2021-01-19 committed to judaicalink-generators
  (`compact-memory-linking/`, `aefa2e5`).
- 2025-06-05 notebooks ported to Python scripts by Benjamin Schnabel (never used to regenerate); 2025-11 moved to
  `legacy/compact-memory-linking/`.

## Kept version 2021-01-18

**Exact**, `aefa2e5`: the committed logic (thresholds 0.6 and 0.4), run on the TagMe pickle and the inverted index of
the legacy entity pages, gives the intermediate `cm_tagme_resource_reference_data` (749,446 mentions) and from it
both Turtle files byte-identical to the kept ones (with rdflib 4.2.2). The committed notebooks differ slightly from
what ran (input path, one unset variable), without effect on the output.

## Inputs

- `cm_entities_tagme.pickle` (TagMe output) and `ep_inv_index.pickle` (legacy entity pages): not in the dumps; on
  the labs VM and in the private backup.
- Raw TagMe output (791,306 JSON files): only on the labs VM (`/data/cm/output/linker/entities/`), backup part 2.
- External: TagMe (D4Science), Wikipedia of 2020.

## Reproduction

The RDF step is reproducible **only from the intermediates**, which are kept in the backup, not in the dumps.
The annotation itself is **not** reproducible (service and knowledge base versions, unseeded language detection).
Mention IRIs (`cm-tagme/<n>`) are positional and cannot be reused across runs.

The copy of `tagme_linker.ipynb` in `original/` has its access token replaced by `<REDACTED>`; otherwise all files
are verbatim.

## Original files

`original/` holds copies of the files below, unchanged unless noted, under `<repository>@<commit>/<path>`. They are the record of what was used; they are not run from here.

| File | Repository | Commit (date, author) | Note |
|---|---|---|---|
| [`compact-memory-linking/cm_tagme_resource_reference_data.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/cm_tagme_resource_reference_data.ipynb) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`compact-memory-linking/cm_tagme_resource_reference_rdf.ipynb`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/cm_tagme_resource_reference_rdf.ipynb) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`compact-memory-linking/README.md`](https://github.com/judaicalink/judaicalink-generators/blob/aefa2e59b8b8743bdcde44b9b612cfa3ff2bdf12/compact-memory-linking/README.md) | judaicalink-generators | `aefa2e5` (2021-01-19, marcorovera) |  |
| [`legacy/scripts/cm/scripts/entity_extraction/tagme_linker.ipynb`](https://github.com/judaicalink/workflow/blob/2c13f6a1fab1131dc909aefcdcb268c6cec59be0/legacy/scripts/cm/scripts/entity_extraction/tagme_linker.ipynb) | workflow | `2c13f6a` (2025-12-16, Benjamin Schnabel) | gcube token redacted in this copy |
| [`legacy/scripts/cm/scripts/jl_linking/tagme2pickle.ipynb`](https://github.com/judaicalink/workflow/blob/2c13f6a1fab1131dc909aefcdcb268c6cec59be0/legacy/scripts/cm/scripts/jl_linking/tagme2pickle.ipynb) | workflow | `2c13f6a` (2025-12-16, Benjamin Schnabel) |  |
