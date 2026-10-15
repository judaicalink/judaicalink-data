# 0027 The store beside the old dumps on archive.judaicalink.org

Status: accepted · Date: 2026-10-13 · Amends [0014](0014-locations-dataindex-finder.md) and [0015](0015-dumps-clean-start.md)

## Context

0015 planned to replace the old dumps on archive.judaicalink.org (`/dumps/`, dumps-clean in the old layout, linked
from the catalogue state `judaicalink-site` `81b42a5`) with the store, and left open whether the old paths redirect.
The download paths were never promised to be stable; the catalogue links to them.

## Decision

- The store is published in its own folder, `https://archive.judaicalink.org/store/` (`<slug>/<version>/<path>`),
  copied unchanged from `lokal/store`. This is the `archive` location in `catalog/locations.toml`.
- The old `/dumps/` stays as it is for now, so links to it keep working; it is not in `locations.toml` and the
  index does not look there. Removing it later needs no redirects.

## Consequences

- Publishing the store and switching the site are independent of cleaning up the old files.
- The archive is updated by adding new version folders to `/store/` (files of a version never change, 0019).
