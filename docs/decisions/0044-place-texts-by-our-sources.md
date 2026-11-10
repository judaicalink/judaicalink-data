# 0044 Place texts are linked to the places our sources name for them

Status: accepted · Date: 2026-11-10 · Amends [0024](0024-which-fix-for-which-error.md)

## Context

geo-enriched links place texts without an IRI to GeoNames features. Its gazetteer (2026-10-16) chose among the
features of a name by population, so a large place that has the name only as an exonym beat the place meant:
Bethlehem as Belém, Jarosław as Yaroslavl, Carlsbad as Carlsbad (California). Our own data says which place a text
means: the GND states the text and the place together for most of its persons.

## Decision

- **Evidence first:** a text that two or more records state together with a place IRI gets the place of at least two
  thirds of them; without such a majority it is ambiguous in our data and not linked.
- **Then the place our data names most often** among the candidates of the name, if it is named at least three times
  as often as the next; else the text is ambiguous. Population decides only among places our data does not name.
- **Wikidata is not evidence:** it is the benchmark the place links are checked against (P19/P20 of the same persons).
- A wrong place for a text is fixed in the generator that chose it, not left to the entity pages (0042).

## Consequences

- geo-enriched and records-normalized are made again; the check against Wikidata is kept in
  `lokal/work/geo-check/check.py` (to become a generator check).
