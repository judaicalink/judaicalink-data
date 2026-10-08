# 0007 Prefer complementary datasets; fix by superseding

Status: accepted · Date: 2026-10-05 (superseding added 2026-10-06)

## Context

Additional information (computed, looked up, AI-generated) should be added without touching the
published data, so that every statement keeps its provenance. Some datasets cannot be fixed by adding,
e.g. the legacy NLI persons, whose generator lost the identity of the records.

## Decision

- **Complementary datasets** only add triples to the graph; existing triples are never changed or
  deleted. Linksets are complementary datasets that only link.
- Where a dataset has to be fixed, a **new dataset supersedes it**: its `-meta` states
  `dcterms:replaces <old dataset>`, the old one is no longer loaded, and its archived dumps stay as they
  are. Published dumps are never edited in place.
- Problems that cannot be fixed by adding are recorded as quality annotations (DQV / Web Annotation).
- Uncertain links are not made.

## Consequences

- Example: `nli-records` supersedes `nli-persons`; `ls-nli-legacy` maps every legacy URI to the records it
  was made from.
- The QLever loader leaves out every dataset that some `-meta` file replaces.
