# 0024 Which fix for which error: new version, correction dataset or complement

Status: accepted · Date: 2026-10-12

## Context

There are now three ways to improve published data: a new version of a dataset (0018, a new version may clean up,
0020), a correction dataset that adds and deletes triples (0023), and a complementary dataset that only adds (0007).
For the first errors found for the entity pages (bhr's links to the EntityFacts service page) a correction dataset
was proposed; the errors turned out to be systematic errors of bhr's generator, with more of them in the same dataset.

## Decision

Choose the fix by the kind of error:

- **A systematic error of one dataset** (one cause, many triples, usually a bug of its generator) → **a new version
  of that dataset.** Its generator is fixed and run again; where the chain that made it cannot be run again (legacy
  datasets), a generator transforms the previous version. Each fix is a parameter with the fix as default, so that
  the faithful output can still be checked (with all fixes off, the previous version's triples); the differences are
  documented in the generator's README and the changelog.
- **Single findings spread over datasets** (curation, tracked issues, an individual wrong link or value) → **a
  correction dataset** (0023).
- **New facts about records** (normalised values, links, enrichments) → **a complementary dataset** (0007).

The datasets made from the corrected one are made again (or, once published, get new versions).

## Consequences

- `bhr` 2026-10-12, made from 2018-10-24 by `generators/bhr/generate.py`: the links to the EntityFacts service page
  (783), the links with empty identifiers (9), empty literals (2,141) and the GND placeholder `"NA"` (1,692) dropped;
  the mixed records of Glückmann and Gunzenhausen (grouped with Gutheim by their empty GND number in 2018) separated;
  `jl:occpation` as `jl:occupationURI` (2,900).
- `records-normalized` and `quality-annotations` (unpublished) are made again from it; records-normalized no longer
  restates bhr's occupation IRIs.
- The first correction dataset waits for the research on the conflations found for the entity pages (0022); the
  one disambiguation link in dbpedia-persons is a candidate.
