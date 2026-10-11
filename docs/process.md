# Process: from development to the catalogue, the dumps locations and Frankfurt

Draft of 2026-10-07, updated 2026-10-08 for [0013](decisions/0013-catalogue-format.md) and
[0014](decisions/0014-locations-dataindex-finder.md), 2026-10-11 for [0019](decisions/0019-dumps-locations-equal.md). It describes how data moves; it will be refined as we
use it. Decisions referred to are in `decisions/`.

## States of a dataset version

| State | Where the data is | Catalogue |
|---|---|---|
| **in development** | local (`lokal/dumps-additions/`), local QLever | not listed (experimental runs are never catalogued) |
| **catalogued** | local or already on a dumps location | version added explicitly to the entry, with changelog entry; a preview until `stable` points to it |
| **published** | at one or more dumps locations, `<location>/<slug>/<version>/<path>` (archive.judaicalink.org, mannheim.judaicalink.org; loaded in the Mannheim SPARQL endpoint where useful) | found by the index, appears in `dataindex.json` and the finder |
| **in Frankfurt** | in their catalogue / dumps | found by the index (their catalogue page; their files once they use the same structure); we keep no marker |
| **superseded** | dumps stay unchanged, may be pruned later | the successor's entry has `replaces`; `replaced_by` is derived |
| **pruned** | no longer at any public location; we still keep a copy unless decided otherwise | changelog entry |

The dumps locations are equal and none promises completeness or permanence; the files of a version are never
changed wherever they are (except `-meta`), and the git history of this repository is the permanent record
([0019](decisions/0019-dumps-locations-equal.md)). archive.judaicalink.org is the location web.judaicalink.org
links to; it currently holds the catalogue state `judaicalink-site` `81b42a5` (identical to what Frankfurt
loaded), in the old layout until `lokal/dumps-new` replaces it. Everything we produced since 2026-10-05 is
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

## 3. Publishing at a dumps location

1. Copy the files to `<location>/<slug>/<version>/<path>`: mannheim.judaicalink.org for versions shown on the
   Mannheim platform (previews included), archive.judaicalink.org for versions web.judaicalink.org should offer.
   The structure is the same everywhere, so files can be copied between locations unchanged
   ([0014](decisions/0014-locations-dataindex-finder.md)).
2. Where useful, load them into the Mannheim SPARQL endpoint; update the demonstrators.
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

## 5. Keeping and pruning

Every file of a catalogued version is kept by us in at least one place (a dumps location or the store, the
backed-up, non-public structure of [0019](decisions/0019-dumps-locations-equal.md), which also holds full acquisition
outputs and private inputs). Which
versions a location offers can change: a location may drop versions, and historical versions, above all
superseded ones, may be pruned from all public locations at some point. Pruning gets a changelog entry; before
a version is pruned, check that nothing depends on what only it contains ([0019](decisions/0019-dumps-locations-equal.md)).
When to prune is not decided yet.

## Checklist for every change

- [ ] Slug, namespace, kind of change decided; decision record written if a convention is set
- [ ] Generator in the repository, deterministic, `-meta` written
- [ ] Loaded and checked locally; numbers in the `-meta` description
- [ ] Catalogue entry: version added explicitly (on request), changelog, `stable` moved if it is the
      recommended version; `catalog.py check`, `index`, `sync`
- [ ] Entity pages rebuilt if records changed
- [ ] Dashboard / demonstrators updated
- [ ] Published on mannheim.judaicalink.org (when agreed); offered to Frankfurt (when ready)
