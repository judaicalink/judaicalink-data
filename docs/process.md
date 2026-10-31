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
| **pruned** | no longer at any public location; kept in the pruned area (`lokal/pruned`, 0041) | `pruned = "<date>"` on the version, changelog entry |

The dumps locations are equal and none promises completeness or permanence; the files of a version are never
changed wherever they are (except `-meta`), and the git history of this repository is the permanent record
([0019](decisions/0019-dumps-locations-equal.md)). archive.judaicalink.org is the location web.judaicalink.org
links to; it currently holds the catalogue state `judaicalink-site` `81b42a5` (identical to what Frankfurt
loaded), in the old layout in `/dumps/`; the store (`lokal/store`) goes beside it in `/store/`, the archive location of the index
([0027](decisions/0027-store-beside-the-old-dumps.md)). Everything we produced since 2026-10-05 is
*in development*.

## 1. Developing a dataset

1. **Decide the kind of change** ([0007](decisions/0007-complementary-and-superseding-datasets.md)):
   complementary dataset (only adds), new dataset, or a successor that supersedes an existing one.
   Superseding needs a reason that adding cannot solve; record it in the catalogue changelog.
2. **Choose slug and namespace.** Slug = file name of the catalogue entry = graph name. New resources get
   URIs in `http://data.judaicalink.org/data/<namespace>/…` ([0002](decisions/0002-uris.md)); facts go
   about records and the entity they concern ([0008](decisions/0008-facts-about-records.md)).
3. **Write the generator** `generators/<slug>/generate.py` in `judaicalink-data` (standard library Python,
   deterministic, ignoring its own earlier output, web answers cached: [0011](decisions/0011-reproducible-generation.md);
   interface: [0018](decisions/0018-generator-framework.md)). It writes the data files (`<slug>.ttl.gz`), never
   metadata.
4. **Run, compare, check**: `jl generate <slug>` (a run in the build area), `jl compare` with the kept version,
   `jl show-canonical`; load into the local endpoint where useful (counts, examples, effect on the entity pages,
   dashboard). Fix and rerun until the numbers are understood. No versions while working: runs only.
5. **Document**: catalogue entry (draft), README of the generator folder, decision record if a convention is set
   or an exception made.
6. **Make it a version, on request**: commit the code, run again, then `jl add-version <slug>/<run-id>` (try
   `--dry-run` first): header comments, the `-meta` (VoID/DCAT/PROV, rendered from the entry, the run record and
   the measured statistics), the run record `generators/<slug>/runs/<version>.json`, the version and a changelog
   entry in the catalogue, the files in the store. Review and commit; move `stable` by hand when it is the
   recommended version. `jl render-meta <slug>/<version>` renders the `-meta` again after the entry changed.
   One version per piece of work; then `jl clean-runs` deletes the runs that did not become it.

## 2. Entity-page runs

Entity pages are made again after changes to the records ([0009](decisions/0009-entity-pages.md),
[0022](decisions/0022-entity-pages-in-the-framework.md)): a new version of `ep`.

1. Make the datasets that changed as versions; set the inputs of `generators/ep/generate.py` (`STABLE`, the previous
   version of `ep`) to the stable versions.
2. `./jl generate ep`. The generator checks that every IRI of the previous version is a page or in the history, and
   that records known to be different are not joined again.
3. Read the run log: groups with several Wikidata items or incompatible classes, keys shared by many records of one
   dataset, the splits and merges. Wrong links are fixed in the data (0024: a new version of the dataset or a
   correction in a correction dataset), then the run is repeated.
4. `./jl add-version ep/<run>`; update the counts in `generators/ep/README.md`, the dashboard and the demonstrators.

## 2a. Authority datasets: the cascade

The authority datasets (`gnd`, `lc`, `geonames`, `viaf`, `wikidata`, `dbpedia`) select their records from our datasets
and from each other ([0029](decisions/0029-identity-from-our-linksets.md)). When a record dataset or an authority
input changes (`jl check-authorities` lists the identifiers an authority dataset lacks):

1. `jl cascade <dir>` (`src/jl/cascade.py`). The seeds: every identifier of an authority source that our record
   datasets name (any statement), the linksets that are not made from the authority datasets (2014links, interlinks,
   ls-nli-legacy, …), and the static lists of each authority dataset (`SEEDS` in its `generate.py`, or the seeds its
   `lookup.py` gives: the GND lists, the dbpedia-persons articles, the Wikidata items that state the identifier of a
   record of ours). Then a worklist, until nothing is pending: each authority resolves its new identifiers to the
   current ones and gives the declared identity links of these records
   ([0032](decisions/0032-identity-declarations.md)); an identifier of another source that is not yet
   selected becomes pending there; Wikidata is also searched by the GND, VIAF, LC, GeoNames and ISNI numbers. Each
   authority takes part with `generators/<slug>/lookup.py` (`resolve`, `links`, `search`, `seeds`, `write`); the
   dumps are read through indexes built once per dump in `<build>/_index/`, Wikidata and Wikipedia are asked online
   with caches in the work dir. Selections only grow. With the indexes in place, a cascade takes about two minutes
   (2026-10-19: 8 rounds).
2. `jl add-input cascade/<date> <dir>/* --move` and set `CASCADE` in `src/jl/cascade.py` to it: the authority
   generators read their selection (`<slug>-selection.tsv.gz`) and the answers (`entities.jsonl.gz`,
   `titles-<lang>.jsonl`) from this input.
3. `jl generate <slug>` once for each authority dataset, then the linksets (`ls-gnd`, …, `ls-dbpedia`) with
   `--use <slug>/<run>` for the authority runs, then `jl add-version` with all these runs in one call, one version id
   for all. Then the entity pages (2).

The cascade replaced rounds of whole generator runs, which were slow and, run in parallel, oscillated.

## 3. Publishing at a dumps location

1. Copy the files to `<location>/<slug>/<version>/<path>`: mannheim.judaicalink.org for versions shown on the
   Mannheim platform (previews included), archive.judaicalink.org for versions web.judaicalink.org should offer.
   The structure is the same everywhere, so files can be copied between locations unchanged
   ([0014](decisions/0014-locations-dataindex-finder.md)).
2. Where useful, load them into the Mannheim SPARQL endpoint; update the demonstrators.
3. Catalogue: add the changelog entry; run `jl update-dataindex` (records where the files are found) and
   `jl sync-site` for the sites whose catalogue has the entry. A new dataset appears on a site only when
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
Which versions are pruned: [0041](decisions/0041-pruning.md) (the oldest, the newest and one per month stay public); a
pruned version stays in the catalogue (`pruned`), its files move to the private pruned area.

## Checklist for every change

- [ ] Slug, namespace, kind of change decided; decision record written if a convention is set
- [ ] Generator in the repository, deterministic, committed; run compared and checked
- [ ] Version added explicitly (on request) with `jl add-version` (`-meta`, run record, catalogue version and
      changelog); `stable` moved if it is the recommended version; `jl check-catalog`, `update-dataindex`, `sync-site`
- [ ] Entity pages rebuilt if records changed
- [ ] Dashboard / demonstrators updated
- [ ] Published on mannheim.judaicalink.org (when agreed); offered to Frankfurt (when ready)
