# 0019 Dumps locations are equal; the git history is the permanent record

Status: accepted · Date: 2026-10-11 · Supersedes [0005](0005-dumps-archive-and-mannheim.md); amends
[0015](0015-dumps-clean-start.md) · Amended by [0021](0021-store-and-inputs-area.md) (the store is the dumps; inputs in an inputs area)

## Context

[0005](0005-dumps-archive-and-mannheim.md) made archive.judaicalink.org the place for long-term preservation,
whose files are never changed, and [0015](0015-dumps-clean-start.md) repeated that after the clean start. The
name suggested it, but it is not what the location is for: archive.judaicalink.org is the dumps location that
web.judaicalink.org links to. It is meant to hold a clean version of the data, and it gets new versions as we
go on, also of old datasets. Data access is distributed over several locations
([0014](0014-locations-dataindex-finder.md)): archive.judaicalink.org, mannheim.judaicalink.org and Frankfurt.

## Decision

- **All dumps locations are equal.** Each uses `<slug>/<version>/<path>`. None promises to be complete or to
  stay unchanged: a location may add versions, drop versions, or go away. archive.judaicalink.org is the
  location linked from web.judaicalink.org, with a clean selection of versions; mannheim.judaicalink.org is
  the location of the Mannheim platform; Frankfurt has its own. The name "archive" is kept.
- **What is fixed is the version, not a location.** The files of a version are never changed, wherever they
  are (the one exception is the `-meta` file, [0018](0018-generator-framework.md)); version ids are never reused
  ([0013](0013-catalogue-format.md)). A copy is verified by its checksum.
- **The permanent record is the git history of `judaicalink-data`:** which versions existed, their files with
  sizes and checksums, how each was made (generators, run records) and what changed (changelog).
- **We do not lose data:** every file of a catalogued version is kept by us in at least one place (a dumps
  location or the store, below). Historical versions, above all those superseded by later data, may be pruned at some
  point; pruning is recorded in the changelog. Before a version is pruned, check that nothing depends on what
  only it contains (e.g. the old URIs of the legacy entity pages and `nli-persons`, [0010](0010-nli-exception.md)).

### Public dumps stay lean; everything else is in the store

- The public dumps hold what is needed to use the data and to understand it, at a reasonable size. Size matters
  even for uncritical data: a file goes into the public dumps only when it is worth it there.
- *Amended by [0021](0021-store-and-inputs-area.md): the store holds exactly the files of the catalogued versions,
  all published; what is not published is an input in the inputs area. The two points below are kept as history.*
- Whether a file (above all an input or an acquisition output) is published or only kept in the store is decided
  per file. The decision can be reversed at any time: it only decides where the file is. A file in the store is
  referenced by its checksum, like any other; publishing it later means copying it to a dumps location and adding
  it to its version in the catalogue (changelog entry), which changes no file.
- What we keep but do not publish (full acquisition outputs, private inputs, pruned versions, backups of
  locations) is in **the store**: a documented structure, backed up, not public, so that we can find any data
  of any catalogued version, also on request from outside. It has the same layout as the dumps,
  `<slug>/<version>/<path>`, so a version is complete in one place; the run records name what is in it by
  checksum ([0018](0018-generator-framework.md)).
- Where the store lives and how it is backed up is documented with the backup (open issue); it is not named in
  entries or `-meta` files.

## Consequences

- 0005 is superseded (its location rules were already replaced by 0014). In 0015, "files on the archive are
  never changed; removing versions needs a new decision" is replaced by this record.
- "Archived" is no longer a state of a version: a version is published at one or more dumps locations, which
  the index records ([0014](0014-locations-dataindex-finder.md)). `docs/process.md` follows this.
- "The old dumps stay" in [0007](0007-complementary-and-superseding-datasets.md) and 0010 means they are not
  edited; they may be pruned under the rule above.
- Persistent identifiers such as DOIs (open question of 0013) would need a location that promises permanence
  (e.g. Zenodo); none of ours does.
- How a pruned version is shown in the catalogue entry is decided when it first happens.
