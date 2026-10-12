# 0023 Correction datasets: additions and deletions, applied last

Status: accepted · Date: 2026-10-12

## Context

Wrong data (tracked issues, manual curation, inconsistencies found with AI) must be correctable without
regenerating a dataset, and a correction must survive the regeneration of the dataset it corrects. Complementary
datasets (0007) can only add triples; some fixes need deletions (e.g. links to things that are not one entity,
0022). Considered and rejected: minor versions of the corrected dataset with diff sets (no real difference to a new
version, and a regenerated dataset would lose them); deletions as reified statements (hard to read); RDF-star (not a
standard yet, rejected by QLever).

## Decision

- **A new kind `correction`:** a dataset that adds triples and deletes triples. The additions are its data, in its
  own graph; the deletions remove the triples from every graph that contains them. Corrections are datasets with
  versions like all others; the version mechanism is unchanged.
- **Files:** `<slug>.ttl.gz` (the additions) and `<slug>-deletions.ru.gz`: the deletions as SPARQL 1.1 Update
  (`application/sparql-update`, extension `.ru` as registered with that media type; gzipped like every file), always
  in one form, with prefixes and comments allowed:

  ```sparql
  # why these triples are deleted
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  DELETE { GRAPH ?g { ?s ?p ?o } }
  WHERE {
    VALUES (?s ?p ?o) {
      (<http://data.judaicalink.org/data/bhr/Oppenheim_David> owl:sameAs <http://www.dnb.de/DE/Service/DigitaleDienste/EntityFacts/entityfacts_node.html>)
    }
    GRAPH ?g { ?s ?p ?o }
  }
  ```

  Only explicit triples, no patterns (a pattern would also delete what later versions add); a tool may generate the
  rows from a pattern. Any endpoint can run the file as it is; it cannot be loaded as data by accident.
- **Loading:** corrections are applied after all other datasets, and again after any dataset is (re)loaded
  (deletions are idempotent). Among corrections the order does not matter: no correction adds a triple that another
  deletes; a correction is corrected by a new version of its own dataset. Correcting a dataset that is not loaded does
  no harm. Our loader does this; other implementations must do the same (documented with the catalogue).
- **Versions are complete:** a version holds all corrections of its dataset that still apply.
- **Provenance per version, not per triple:** the changelog entry and `refs` (issues, decisions) of the version and
  its `-meta`; comments in both files for readers. A stream of corrections with its own provenance gets its own
  correction dataset.

## Consequences

- The framework: generators read their inputs with the deletions of the stable correction versions applied (named in
  the run record); `check-catalog` checks that every deleted triple is in some stable version (stale ones are
  reported) and that no correction adds what another deletes, and derives which datasets a correction concerns; the
  input preparation for QLever removes the deleted triples; `.ru.gz` files are files of a version
  (`application/sparql-update` in the `-meta`). `correction` goes into `catalog/vocabulary.toml`.
- The first correction dataset holds the two non-identifiers found for the entity pages (0022).
