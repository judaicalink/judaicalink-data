# 0015 Clean start of the dumps: the published version, plus richer earlier ones

Status: accepted · Date: 2026-10-09 · Supersedes in part [0005](0005-dumps-archive-and-mannheim.md) (files on
the archive are not changed: one exception, this restructuring) · Amended by [0019](0019-dumps-locations-equal.md) (no location is permanent) and [0018](0018-generator-framework.md) (labs self-descriptions), [0027](0027-store-beside-the-old-dumps.md) (store beside the old dumps)

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

- The dumps start afresh in the layout `<slug>/<version>/<path>` ([0014](0014-locations-dataindex-finder.md)).
  Every version of dumps-clean is kept. Other older versions are not kept and not reconstructed; the people
  who worked on them are credited in the changelog ([0013](0013-catalogue-format.md)).
- Where the server or its backups hold a richer version than dumps-clean, it is kept as well and is the
  stable version; the other one stays as a newer (preview) or older version, since the reasons for the
  changes are not known:
  - footprints: stable 2024-03-18 (from the backup; titles, owners, places, …), newer 2025-03-21 (only names);
  - haskala: stable 2019-07-01 (enriched), newer 2025-03-24 (most dates and places missing; with
    `Haskala_net.ttl`, the second file of that run, which dumps-clean lacked);
  - stolpersteine (slug `stolperstein` until [0017](0017-slug-stolpersteine.md)): stable 2020-10-06 (judaicalink-labs, 223 persons), older 2018-11-26 (180 persons, with
    scope notes).
- The ontology has one version, 2025-11-27, the current ontology (the archived file held the ontology of
  2020 by mistake).
- Files that were on the server but not in the catalogue are added to their version where they belong: the
  EntityFacts links of bhr, the raw crawls of rujen, yivo and stolpersteine (inputs of the generators).
- Removed from the catalogue, as test data or derived from other datasets: `cmtest` (a test sample of the
  Compact Memory full text for Elasticsearch), `ep-supp` (indexes of the legacy entity pages, which
  `ep-2026-10-06` replaces), `cm-tagme-supp` (the raw TagMe output, mostly noise, and a pickle duplicating
  `cm-tagme`), `rujen-translation-supp` (caches holding the translations of `rujen-translation`),
  `beacon-persons` (now produced by Frankfurt); from `compact-memory-supp` the pickle duplicating
  `compact-memory` (its page metadata CSV, an input of `cm-structure` and `cm-journals`, stays).
- Every file is a single file; the tar archives named `.gz` (epidat, `ep_GND_ids.json.gz`, haskala, ontology),
  each holding one file, are replaced by plain gzip files with the same content.
- The tree is built by `catalog.py collect` from local copies, finding each file by its checksum; locally it
  is `lokal/dumps-new` (since 2026-10-11 `lokal/store`, the store of [0019](0019-dumps-locations-equal.md)). It replaces dumps-clean on archive.judaicalink.org when it is published (on request). *Amended by [0027](0027-store-beside-the-old-dumps.md): published in `/store/` beside the old `/dumps/`, which stays for now.*
- `labs:/data/dumps` stays until the new tree is published and checked. Then only the backups of 2025-02-06
  (git history) and 2025-12-19 (last state) are kept, offline and unpublished; everything else in `/data/dumps` is
  deleted. The rest of the VM is not touched by this decision; what to keep from it goes into a separate, private
  backup (not part of the dumps).

## Consequences

- Frankfurt's catalogue still lists the five removed datasets; they should drop them.
- Links to the old paths on archive.judaicalink.org break unless redirects are set up (open question of 0013). *With 0027 they keep working while `/dumps/` stays.*
- *Replaced by [0019](0019-dumps-locations-equal.md): the files of a version never change, at any location; locations may add
  and drop versions; historical versions may be pruned.* After the clean start, files on the archive are again never changed; versions are added. Removing versions
  later needs a new decision.
- The `-meta` files written by earlier generators (rujen, yivo, stolpersteine, rujen-translation) are kept as
  files of their versions (amended by [0018](0018-generator-framework.md): removed 2026-10-11, replaced by the regenerated `-meta`); the regenerated `-meta` files ([0014](0014-locations-dataindex-finder.md)) are added
  to the versions.
