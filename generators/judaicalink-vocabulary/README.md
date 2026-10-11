# judaicalink-vocabulary: generator

The values of the catalogue fields `kind` and `method` as SKOS concepts (decision 0018), generated from
[`catalog/vocabulary.toml`](../../catalog/vocabulary.toml).

## Framework generator

`generate.py` (2026-10-11): reads the vocabulary (input `repo:catalog/vocabulary.toml`, fixed by the commit like the
code) and writes `judaicalink-vocabulary.ttl.gz`: two concept schemes `datasets/vocabulary/kind` and
`datasets/vocabulary/method`, and for each value a concept `datasets/vocabulary/<field>/<value>` with
`skos:notation` (the value as used in the catalogue), English label and definition. A withdrawn value gets
`owl:deprecated` and the reason as `skos:note`. The `-meta` files state the values as `dcterms:type` of a dataset.
