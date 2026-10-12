# cm-ocr-quality: generator

An estimate of the OCR quality of the Compact Memory pages (new dataset, decision 0020).

## History

- 2026-10-05 (Kai Eckert): `cm_ocr_quality` in kg-complements (`datasets_deterministic.py`), the OCR quality estimate of
  the data profile dashboard as a dataset; output in `dumps-additions/cm-ocr-quality/`, never published.

## Framework generator

`generate.py` (2026-10-12): a port of `cm_ocr_quality` without changes to its logic (single process instead of 12).
Inputs: the full-text bundle `inputs:compact-memory/fulltext-2026-10-05-v2` (the page texts) and
`compact-memory/2026-10-12/compact-memory-pages.ttl.gz` (the page IRIs). Gives exactly the 846,808 triples of the
kg-complements output (word list of 116,604 words). About three minutes.
