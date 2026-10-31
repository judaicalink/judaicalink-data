# 0041 Pruning: the oldest, the newest and one version per month

Status: accepted · Date: 2026-10-31 · Amends [0019](0019-dumps-locations-equal.md), [0021](0021-store-and-inputs-area.md)

## Context

The work of October 2026 made many versions of a few datasets (ep five, gnd five), most of them superseded within
days. The dumps location archive.judaicalink.org ran out of space. 0019 allows pruning historical versions and left
open how a pruned version is shown in the catalogue.

## Decision

- **Which versions stay public:** per dataset the oldest version, the newest, and at most one per month in between
  (the last of the month; the newest stands for its own month). Also kept: the stable version, and every version a
  current generator reads as a pinned input (`INPUTS`), so that the generators can run from the store.
- **A pruned version stays in the catalogue** with its files, sizes and checksums, and gets `pruned = "<date>"`; a
  changelog entry names the versions pruned. Its status is `pruned`; it has no location in the data index.
- **Its files leave every public dumps location** (archive.judaicalink.org, mannheim.judaicalink.org) and are kept in
  the pruned area, `lokal/pruned/<slug>/<version>/<path>` (`pruned` in `local.toml`): not public, the layout of the
  store, backed up with it. The store keeps exactly the published files (0021), so copying it to a location never
  brings a pruned version back. Generators read a pruned version from the pruned area.
- Before pruning, check that nothing depends on what only the version contains (0019): the IRIs of earlier entity
  pages are in the history of the newest `ep`.

## Consequences

- First pruning 2026-10-31: bhr 2026-10-16; ep 2026-10-12, 2026-10-19, 2026-10-26, 2026-10-26-2; epidat 2026-10-16;
  geonames 2026-10-19; gnd 2026-10-19, 2026-10-26; lc 2026-10-19; ontology 2026-10-12, 2026-10-17; record-classes
  2026-10-18; rujen 2026-10-16 (293 MB). Kept as pinned inputs: bhr 2026-10-12, epidat 2026-10-12, footprints
  2026-10-12 and 2026-10-26, gnd 2026-10-16, viaf 2026-10-19.
- A pruned version can be published again: its files are copied back to the store and to a location, and `pruned`
  is removed (changelog entry).
