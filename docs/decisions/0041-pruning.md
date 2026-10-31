# 0041 Pruning: the oldest, the newest and one version per month

Status: accepted · Date: 2026-10-31 · Amends [0019](0019-dumps-locations-equal.md), [0013](0013-catalogue-format.md)

## Context

The work of October 2026 made many versions of a few datasets (ep five, gnd five), most of them superseded within
days. The dumps location archive.judaicalink.org ran out of space. 0019 allows pruning historical versions and left
open how a pruned version is shown in the catalogue.

## Decision

- **Which versions stay published:** per dataset the oldest version, the newest, and at most one per month in between
  (the last of the month; the newest stands for its own month). Also kept: the stable version; every version that
  the newest or the stable version of any dataset was made from (its run record): above all the previous `ep`, which
  the entity pages are compared with; and every version a current generator reads as a pinned input (`INPUTS`).
- **A pruned version leaves the catalogue entry.** Its changelog entries stay, and its pruning gets one more:
  `version`, the date, `refs = ["0041"]`. Its files, sizes and checksums stay in the git history of the entry, its run
  record in `generators/<slug>/runs/`; its id is not reused. A version that names a pruned version as its input
  stays valid (`check-catalog` finds the pruned version in the changelog).
- **Its files leave every public dumps location** (archive.judaicalink.org, mannheim.judaicalink.org). We keep them
  in `lokal/pruned/<slug>/<version>/<path>`, not public, beside the store, which keeps exactly the published files
  (0021).
- Before pruning, check that nothing depends on what only the version contains (0019): the IRIs of earlier entity
  pages are in the history of the newest `ep`.

## Consequences

- First pruning 2026-10-31: ep 2026-10-12, 2026-10-19, 2026-10-26; ontology 2026-10-12, 2026-10-17; record-classes
  2026-10-18 (165 MB). The other October versions stay: they are the newest, stable, monthly, or inputs of the
  newest versions (ep 2026-10-26-2 of ep 2026-10-31, gnd 2026-10-26 of the linksets, …).
- A pruned version can be published again: its entry comes back from the git history, its files from the pruned
  area (changelog entry).
