# ls-nli-legacy: generator

The legacy nli-persons URIs linked to the NLI authority records they were made from (decisions 0010, 0020).

## History

- 2026-10-06 (Kai Eckert): `ls_nli_legacy` in kg-complements (`nli_records.py`); output in `dumps-additions/`, never
  published.

## Framework generator

`generate.py` (2026-10-12): a port without changes to its logic, using `nli_export.py` of nli-records as shared code.
Inputs: `inputs:nli/authority-export-2019/auth.json.gz` and `nli-persons/2019-01-25`, against which the reproduction of
the legacy URI assignment is checked (all 182,445 URIs, else the run fails). With
`--param data_annotation_iris=false` it gives exactly the 623,077 triples of the kg-complements output.

The fix (default): the 4,367 quality annotations get IRIs in the namespace of the dataset,
`data/ls-nli-legacy/annotation/<hash>`, instead of `datasets/ls-nli-legacy/a/<hash>`, which is the space of the
dataset's versions and metadata (decisions 0002, 0018); 26,202 triples change their subject or object, nothing else.
About 15 seconds.
