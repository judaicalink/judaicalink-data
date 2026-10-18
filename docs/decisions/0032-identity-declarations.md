# 0032 Identity declared per dataset; identifiers checked; link quality measured

Status: accepted (the parts under "to come" proposed) · Date: 2026-10-18

## Context

The first cascade of the authority datasets (0029) and the entity-page tests of 2026-10-18 joined records wrongly in
three ways: through properties that do not state identity (a place of birth of a GND record selected Essen, then
Nordrhein-Westfalen); through IRIs that identify nothing (8,141 VIAF clusters link `http://data.bnf.fr/#foaf:Person`,
which joined 39,429 records into one entity); and through sources that link a person to the record of one of his
works. Which properties state identity depends on how a source uses them; a fixed list for all datasets is wrong.

## Decision

- **Declared identity:** the catalogue entry of each dataset names the properties that state identity and the
  sources they point to (field `identity`: `"owl:sameAs" = ["gnd", "viaf"]`; sources of `jl.identifiers.SOURCES`,
  `judaicalink` for our own records). The cascade, the linksets, the link check and the entity pages use only these;
  a dataset without a declaration states no identity. The declarations are made from the evidence of each source
  (`docs/reports/2026-10-18-identity-survey.md`).
- **Link quality:** every declared property is measured per dataset and target (`jl sample-links`, `jl
  link-quality`): a random sample (or all links of a small unit) with the evidence of both sides, judged correct,
  wrong or undecidable; the accuracy correct / (correct + wrong) with its 95% interval
  (`docs/reports/2026-10-18-link-quality.md`). The results are kept in `catalog/link-quality.toml`. **Threshold**
  (decided 2026-10-18): a unit joins records (linksets, entity pages) if its accuracy is at least 95% and, where
  only a sample was checked, the lower bound of the interval at least 90%; below, its links are kept as links but join
  nothing. A unit not measured joins. First result: below are haskala → VIAF (37%, matched by name), footprints →
  GND by gndIdentifier (51%, places matched by label), footprints → GND, VIAF, LC (92%, 89%, 0 of 1), 2014links →
  Wikipedia, GeoNames (91%, 92%), geo-coordinates → VIAF (94%, lower bound 86%).
- **GeoNames:** several features of one entity are kept (a city and its municipality: the distinction does not
  matter for us; GeoNames serves to tell places of the same name apart and to give coordinates); the coordinates come
  from the populated place. The entity pages list only pairs that are not closely linked (same name, near each
  other) as conflicts.
- To come (proposed): a link counts only if its target matches the pattern of its source (jl.iris), and a check for
  hubs (one identifier linked from unusually many records) in every run of an authority dataset or linkset; on the
  entity pages, a replaced IRI is never a member and at most one current record per record dataset joins an entity
  (declared exceptions, e.g. geo-coordinates with one record per place name); VIAF and Wikidata link without joining
  unless their quality allows it. Rather too few joins than wrong ones.
