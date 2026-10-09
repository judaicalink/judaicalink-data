# 0015 Clean start of the dumps: one current version per dataset

Status: accepted · Date: 2026-10-09 · Supersedes in part [0005](0005-dumps-archive-and-mannheim.md) (files on
the archive are not changed: one exception, this restructuring)

## Context

With production in Frankfurt, the Mannheim dumps can start afresh. Before September 2026 they were served
from `labs:/data/dumps` (data.judaicalink.org/dumps): 225 files and 4.1 GB, with uncompressed duplicates,
older versions, logs, test files and four complete backups (3.3 GB; the oldest with the git history of the
dumps, 2023-05 to 2025-01). archive.judaicalink.org/dumps ("dumps-clean", `lokal/dumps`) holds only the 82
files the catalogue links to, in the old layout. The inventory of 2026-10-09 compared the three
(`lokal/work/dumps-inventory/OVERVIEW.md`) and found data that would be lost: richer earlier versions of
footprints and haskala than the ones published, a newer stolpersteine, EntityFacts links for bhr and the raw
crawls behind rujen, yivo and stolpersteine.

## Decision

- The dumps start afresh in the layout `<slug>/<version>/<path>` ([0014](0014-locations-dataindex-finder.md)),
  with **one version per dataset**, the one the catalogue names. Older versions are not kept and not
  reconstructed; the people who worked on them are credited in the changelog ([0013](0013-catalogue-format.md)).
- The version kept is the best one available, not necessarily the last published:
  - footprints: 2024-03-18 (from the backup; the regeneration of 2025-03-21 has only names);
  - haskala: the enriched version of 2019 (the regeneration of 2025-03-24 lacks dates and places);
  - stolperstein: the judaicalink-labs version of 2020-10-06 (223 persons instead of 180);
  - ontology: 2025-11-27, the current ontology (the archived file held the ontology of 2020).
- Files that were on the server but not in the catalogue are added to their version where they belong: the
  EntityFacts links of bhr, the raw crawls of rujen, yivo and stolpersteine (inputs of the generators).
- Every file is a single file; the tar archives named `.gz` (epidat, `ep_GND_ids.json.gz`, haskala, ontology)
  are replaced by plain gzip files with the same content.
- The tree is built by `catalog.py collect` from local copies, finding each file by its checksum; locally it
  is `lokal/dumps-new`. It replaces dumps-clean on archive.judaicalink.org when it is published (on request).
- `labs:/data/dumps` stays until the new tree is published and checked. Then only the backups of 2025-02-06
  (git history) and 2025-12-19 (last state) are kept, offline and unpublished; everything else there is deleted.

## Consequences

- Links to the old paths on archive.judaicalink.org break unless redirects are set up (open question of 0013).
- After the clean start, files on the archive are again never changed; versions are added. Removing versions
  later needs a new decision.
- The `-meta` files written by earlier generators (rujen, yivo, stolpersteine, rujen-translation) are kept as
  files of their versions; the regenerated `-meta` files ([0014](0014-locations-dataindex-finder.md)) are added
  to the versions.
