# 0016 SPARQL endpoint and data access are not part of judaicalink-data

Status: accepted · Date: 2026-10-10 · Amends [0003](0003-judaicalink-data-repository.md) (`qlever/` does not move here)

## Context

0003 planned to move the QLever setup (`../qlever/`, Qleverfile from catalogue and dumps, queries) into
`judaicalink-data`. QLever was tried to build demonstrators and data access, not to generate data.

## Decision

- `judaicalink-data` is only about generating the data files and describing them in the catalogue
  (generators, catalogue, decisions, process).
- SPARQL endpoints, demonstrators and other data access belong to the platform (mannheim.judaicalink.org) and are
  taken up together with it, once the data is clean.

## Consequences

- `../qlever/` stays outside this repository for now; consumers of the catalogue such as a Qleverfile builder
  read the catalogue from here.
- Rebuilding `ontology-complements` and loading the new ontology into an endpoint wait for the platform work.
