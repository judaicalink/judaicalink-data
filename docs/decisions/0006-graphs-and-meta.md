# 0006 One file = one named graph = dataset IRI; -meta files with provenance

Status: accepted, amended by [0018](0018-generator-framework.md) (graph names) · Date: 2026-10-05

## Context

The archived catalogue named "graphs" like `http://data.judaicalink.org/data/yivo`, which are namespaces of
resources, not graphs. Provenance of the datasets was incomplete and inconsistent.

## Decision

- *Amended by 0018: all RDF files of a version form one graph, the dataset IRI; the metadata graph is
  `datasets/<slug>/meta`, not `datasets/<slug>-meta`.*
- Every data file is one named graph. Graph IRI = dataset IRI = `http://data.judaicalink.org/datasets/<slug>`,
  `<slug>` = the catalogue entry's file name. `http://data.judaicalink.org/data/<x>/` is a namespace for
  resources, not a graph; several graphs may describe resources of the same namespace.
- Every data file `<slug>.ttl.gz` has a `<slug>-meta.ttl.gz` (graph `…/datasets/<slug>-meta`) with the
  dataset description (VoID, DCAT, PROV: title, description, creator, licence, dumps, statistics,
  generation activity, script, inputs) and the provenance of the metadata itself.
- Existing datasets get `-meta` files generated from the catalogue entry, measured statistics and the
  generator scripts; existing self-descriptions are left as they are.
- Files are gzipped N-Triples (valid Turtle).

## Consequences

Details and the generator: `kg-complements/README.md` (to move into this repository).
