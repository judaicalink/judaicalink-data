# nli-records: generator

The person and work records of the NLI authority export behind nli-persons, one resource per record; supersedes
nli-persons (decisions 0007, 0010, 0020).

## History

- 2026-10-06 (Kai Eckert): `nli_records` in kg-complements (`nli_records.py`), re-extracting the export that
  nli-persons was made from (`legacy/nli-persons/input/auth.json.gz` of judaicalink-generators, committed by Maral
  Dadvar in 2019); output in `dumps-additions/`, never published.

## Framework generator

`generate.py` (2026-10-12): a port without changes to its logic. The reading of the export, the record IRIs, the
legacy URI assignment and the matching of works to persons are in `nli_export.py`, which ls-nli-legacy loads as
shared code (`jl.generator.load_shared`). Input: `inputs:nli/authority-export-2019/auth.json.gz`. Gives exactly the
1,523,575 triples of the kg-complements output (183,281 person and 1,908 work records; 37,597 subject headings left
out). IRIs built from source text are percent-encoded as in kg-complements (one LC number of the export is garbage,
`|azannaab|||||d`). About 15 seconds.
