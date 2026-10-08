# Process: from development to the catalogue, mannheim.judaicalink.org, Frankfurt and the archive

Draft of 2026-10-07, updated 2026-10-08 for [0013](decisions/0013-catalogue-format.md) and
[0014](decisions/0014-locations-dataindex-finder.md). It describes how data moves; it will be refined as we
use it. Decisions referred to are in `decisions/`.

## States of a dataset version

| State | Where the data is | Catalogue |
|---|---|---|
| **in development** | local (`lokal/dumps-additions/`), local QLever | not listed (experimental runs are never catalogued) |
| **catalogued** | local or already on a dumps location | version added explicitly to the entry, with changelog entry; a preview until `stable` points to it |
| **published** | `mannheim.judaicalink.org/dumps/<slug>/<version>/<path>`, loaded in the Mannheim SPARQL endpoint | found by the index, appears in `dataindex.json` and the finder |
| **in Frankfurt** | in their catalogue / dumps | found by the index (their catalogue page; their files once they use the same structure); we keep no marker |
| **archived** | `archive.judaicalink.org/dumps/<slug>/<version>/<path>` (files never changed afterwards) | found by the index; nothing changes in the entry |
| **superseded** | dumps stay | the successor's entry has `replaces`; `replaced_by` is derived |

The archive currently holds the versions identical to Frankfurt (catalogue state `judaicalink-site`
`81b42a5`; to be restructured to `<slug>/2026-09-26/<path>`). Everything we produced since 2026-10-05 is
*in development*.

## 1. Developing a dataset

1. **Decide the kind of change** ([0007](decisions/0007-complementary-and-superseding-datasets.md)):
   complementary dataset (only adds), new dataset, or a successor that supersedes an existing one.
   Superseding needs a reason that adding cannot solve; record it in the catalogue changelog.
2. **Choose slug and namespace.** Slug = file name of the catalogue entry = graph name. New resources get
   URIs in `http://data.judaicalink.org/data/<namespace>/…` ([0002](decisions/0002-uris.md)); facts go
   about records and the entity they concern ([0008](decisions/0008-facts-about-records.md)).
3. **Write the generator** in `judaicalink-data` (standard library Python, deterministic, ignoring its own
   earlier output, web answers cached: [0011](decisions/0011-reproducible-generation.md)). It writes
   `<slug>.ttl.gz` and `<slug>-meta.ttl.gz` (VoID/DCAT/PROV, [0006](decisions/0006-graphs-and-meta.md)).
4. **Build, load, check** in the local QLever endpoint: counts, examples, effect on the entity pages,
   dashboard. Fix and rebuild until the numbers are understood.
5. **Document**: catalogue entry (draft), README of the dataset where it is complex, decision record if a
   convention is set or an exception made.

## 2. Entity-page runs

Entity pages are rebuilt after changes to the records ([0009](decisions/0009-entity-pages.md)):

1. Build and load all record and complementary datasets (order: `kg-complements/README.md`).
2. Set `PREVIOUS_SETS`/`REPLACES` to the current set, run `EP_SLUG=ep-<date> python3 build.py entity-pages`.
3. Check: every URI of the previous set is still present (unless a decided exception applies), every pointer
   leads to an active page, the run report (merges, splits, refused merges) is plausible.
4. Write the README of the set (counts, changes, obsolete dumps), update dashboard and demonstrators.

## 3. Publishing on mannheim.judaicalink.org

1. Copy the files to `mannheim.judaicalink.org/dumps/<slug>/<version>/<path>` (the same structure on every
   location, so they can move to the archive unchanged: [0014](decisions/0014-locations-dataindex-finder.md)).
2. Load them into the Mannheim SPARQL endpoint; update the demonstrators.
3. Catalogue: add the changelog entry; run `catalog.py index` (records where the files are found) and
   `catalog.py sync` for the sites whose catalogue has the entry. A new dataset appears on a site only when
   its entry file is copied there (0014).
4. Announce on web.judaicalink.org (news) where it matters to others.

## 4. Handover to Frankfurt

1. Offer the dataset version (catalogue entry, dumps, changelog, generator) to the FID team; they have the
   catalogue and its documentation.
2. Frankfurt adopts it by hand, in their catalogue and their production system, and may curate it further.
3. Nothing is marked in our entry: the index shows what their catalogue lists.

New data from Frankfurt is taken over the same way in the opposite direction: by hand, with a catalogue entry
and changelog. There is no automated synchronisation.

## 5. Archiving

A published version is archived on archive.judaicalink.org when it is adopted by Frankfurt or when it is to be
preserved for other reasons: its files are copied to `<slug>/<version>/<path>` there, the next index run
finds them, and a changelog entry records it. Archived files are never changed. The archive does not hold
every version. When to archive is still to be decided.

## Checklist for every change

- [ ] Slug, namespace, kind of change decided; decision record written if a convention is set
- [ ] Generator in the repository, deterministic, `-meta` written
- [ ] Loaded and checked locally; numbers in the `-meta` description
- [ ] Catalogue entry: version added explicitly (on request), changelog, `stable` moved if it is the
      recommended version; `catalog.py check`, `index`, `sync`
- [ ] Entity pages rebuilt if records changed
- [ ] Dashboard / demonstrators updated
- [ ] Published on mannheim.judaicalink.org (when agreed); offered to Frankfurt (when ready)
