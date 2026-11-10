# 0045 Conflicting statements are quality annotations of the records

Status: accepted · Date: 2026-11-10

## Context

An entity page shows one value per fact, taken by precedence (0022, 0042). Where the sources disagree, the page shows
one of them and nothing says that others differ; the text of one record may stand beside the place IRI of another.
Marking single statements as conflicting would need reification or RDF-star, which we chose against before (0023).

## Decision

- A conflict is a resource of its own: a `dqv:QualityAnnotation` and `oa:Annotation` with `dcterms:type "conflict"`,
  the records that state a value as `oa:hasTarget`, the property as `jl:onProperty` (new term), the values per record
  in `oa:bodyValue`. The values stay in the records.
- It is about records, never about entity pages (0008); the pages and the platform find it through their records.
- The dataset `conflicts`, made after ep from the stable ep and the stable sources; ep does not read it.
- First: persons, years and places of birth and death. Years more than a year apart; dates marked uncertain left
  out. Places more than 25 km apart, both settlements. Only facts the sources state; derived place links are fixed in
  their generators (0044).

## Consequences

- 3,285 conflicts in ep 2026-11-10. 308 of them join two records of one authority on one page: a list for checking
  the identity links.
