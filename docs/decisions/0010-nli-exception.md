# 0010 Exception: legacy NLI entity pages are not carried over

Status: superseded by [0022](0022-entity-pages-in-the-framework.md) (the legacy NLI pages are handled by the comparison through `ls-nli-legacy`) · Date: 2026-10-06

## Context

The legacy generator of `nli-persons` (2019) coined URIs from name headings and dropped the record
identifiers: different people with the same name share a URI, one person has several URIs, works and
subject headings became persons. `nli-records` supersedes it ([0007](0007-complementary-and-superseding-datasets.md)).
182,445 legacy entity pages were built on it. Carrying them over as merge or split pointers would keep a
large, misleading history for URIs that, as checked on 2026-10-06, each had one legacy NLI URI as their only
record, no external identifier, and are mentioned by no other dataset.

## Decision

- Entity pages built only on a superseded dataset are **not carried over at all**, not even as pointers.
  This is applied once, to the legacy NLI pages.
- The NLI persons and works get new entity pages from `nli-records`, with numbers above the highest number
  used before, so the old URIs are never reused.
- Information about the old URIs is only in the old dumps (`ep`, `nli-persons`), which stay archived;
  `ls-nli-legacy` maps every legacy NLI URI to the records it was made from.

## Consequences

Exceptions like this one are documented as decisions; the generator applies them through a configured list
(`SUPERSEDED` in `ep_generator.py`), not ad hoc.
