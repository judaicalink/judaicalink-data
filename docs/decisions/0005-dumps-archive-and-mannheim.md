# 0005 Dumps: archive.judaicalink.org for preservation, mannheim.judaicalink.org/dumps for newer versions

Status: accepted, partly superseded by [0014](0014-locations-dataindex-finder.md) (catalogue references to locations) · Date: 2026-10-07

## Context

`archive.judaicalink.org/dumps/` holds the dumps of the catalogue state `judaicalink-site` `81b42a5`, the
state identical to Frankfurt ("dumps-clean", local copy `lokal/dumps/`). New and changed datasets need a
place to be published before or without adoption by Frankfurt.

## Decision

- **archive.judaicalink.org** is the place for the long-term preservation of dump versions. It currently
  holds the version identical to Frankfurt. Files there are not changed.
- **mannheim.judaicalink.org/dumps** publishes newer versions (our additions and replacements).
- The catalogue ([0004](0004-complete-catalogue.md)) points to the archived version when there is one and
  states which version it is, and to the newer version on mannheim.judaicalink.org. *Superseded by
  [0014](0014-locations-dataindex-finder.md): entries name no locations; the index records where versions are.*

## Consequences

- Every dumps location has the structure `<slug>/<version>/<path>`, so files can be moved between
  locations without changing their relative paths; the archive is restructured to it. Entries and `-meta`
  files name no locations ([0014](0014-locations-dataindex-finder.md)).
- How a version on mannheim.judaicalink.org becomes an archived version (when, how named) is part of the
  process (`docs/process.md`).
