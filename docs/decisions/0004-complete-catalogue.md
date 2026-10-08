# 0004 Our catalogue is complete, with changelog and the version identical to Frankfurt

Status: accepted, partly superseded by [0013](0013-catalogue-format.md) and [0014](0014-locations-dataindex-finder.md) (no Frankfurt marker; entries name no locations; format details) · Date: 2026-10-07

## Context

Frankfurt maintains the official catalogue of what is in production. We work on our own version of the
data: mostly through additional datasets, but some datasets have to be fixed or replaced (e.g. the legacy
NLI persons, the entity pages, geo-coordinates). A deviation from the production state is therefore
inevitable, and it must be visible what differs and why.

## Decision

- `judaicalink-data` keeps **one complete catalogue of our data version**: every dataset we use, whether
  taken from Frankfurt unchanged, complemented, superseded or new.
- Format: the TOML front matter of the existing catalogue (`judaicalink-site` / portal `datasets/*.md`),
  so entries can be taken over one to one, extended where needed.
- Every entry has a **changelog** (what changed, when, why, with reference to decisions) and marks the
  **version identical to Frankfurt** (or that there is none yet).
- We still prefer additional (complementary) datasets over changing existing ones
  ([0007](0007-complementary-and-superseding-datasets.md)).

## Consequences

- The catalogue entries point to the dump locations of [0005](0005-dumps-archive-and-mannheim.md):
  the archived version where it exists (and which version that is), the newer version on
  mannheim.judaicalink.org/dumps.
- The concrete field set (version, changelog, relation to Frankfurt) is to be designed when the catalogue
  is set up.
