# 0008 Facts are stated about records and about the entity they concern

Status: accepted · Date: 2026-10-06

## Context

Several early complementary datasets stated their facts about entity-page URIs (Wikidata data for
Compact Memory entities, DNB entityfacts, Compact Memory presence). Such facts get lost or misattributed
when entity pages are merged or split, and the entity-page generator needed special cases for them.
`cm-structure` stated the date of an issue on each of its 846,500 pages.

## Decision

- Complementary datasets state their facts about **records** (the resources of the source datasets),
  never about entity pages. The entity-page set is the only dataset with data on `…/data/ep/…` URIs; it is
  generated from the records and all their facts.
- Every statement goes to **the entity it is about**: the date of an issue on the issue, not on its pages;
  values that can be derived from a URI (e.g. a page id contained in the page URI) are not stated.

## Consequences

The superseded datasets of 2026-10-05/06 (`ep-wikidata-cm`, `ep-new-gnd-persons`, `ep-cm-presence`, ...)
were recreated on records before publication (`cm-entities-wikidata`, `gnd-persons-entityfacts`,
`cm-entities-presence`).
