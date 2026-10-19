# 0033 Withdrawn datasets

Status: accepted · Date: 2026-10-19

## Context

The catalogue format has a `withdrawn` field for a dataset (0013), but nothing acted on it. 2014links (Silk name
matches of 2014 from yivo and rujen) is below the quality threshold (DBpedia 0.91, GeoNames 0.92; 0032), so the entity
pages no longer use it; most of its targets are gone (Freebase, DM2E, LinkedGeoData, NYTimes) and it cannot be made
again. It still seeded the authority cascade (79 DBpedia titles and 3 GeoNames features came only from it) and would
still be loaded into the graph.

## Decision

- A dataset with `withdrawn` (the reason) is no longer part of the knowledge graph: `jl.generator.stable_inputs`
  leaves it out (cascade seeds, entity pages, every generator that reads the stable versions), the data index carries
  the reason, the loaders of the platform skip it, the site lists it with the deprecated datasets and shows the
  reason. Its versions stay in the store, its `stable` stays as the version to look at.
- `jl generate --use` can still name it explicitly.
- 2014links is withdrawn. Links of yivo and rujen records to GeoNames, Wikidata and Wikipedia are to be made again by
  a new matching with disambiguation, as a linkset of its own.
