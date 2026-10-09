# Open issues

State 2026-10-07. Remove an item when it is solved (with a reference to the decision or commit).

## Setting up

- **Generator tooling** (when the generators move here): generators coin version ids (default
  `YYYY-MM-DD[-n]`, other schemes per dataset possible); the tooling can add the version entry (files,
  sizes, checksums, commit) to the dataset's catalogue entry, **only on request**, so experimental runs are
  not catalogued.
- **Move the generators** (`../kg-complements/`, `../qlever/`) into this repository, change the provenance
  links in the `-meta` files (placeholder `judaicalink-generators/…/kg-complements/`) to `judaicalink-data`,
  create the GitHub repository.
- **Catalogue:** the 36 entries in `catalog/` are migrated to the format of
  [0013](decisions/0013-catalogue-format.md) (2026-10-09, `catalog/migrate_0013.py`; `catalog.py check`
  passes). Next: the hand curation (`kind`, `method`, `namespaces` checked
  against the data, `occupations`, file descriptions), restructuring the archive, entries for our
  new datasets, then adapting judaicalink-site (templates, finder, `dumpLocations`) and handing the catalogue
  and its documentation to Frankfurt.
- **Catalogue, open questions** (0013): redirects from the old archive paths; DOIs for archived versions.
- **mannheim.judaicalink.org:** reproducible setup (SPARQL endpoint, dumps, demonstrators), independent of
  the grown setup of the VM; where the platform code lives; whether a pubby-like frontend is needed.
- **Catalogue tools and finder** ([0014](decisions/0014-locations-dataindex-finder.md)): `catalog.py
  index|sync`, the finder page and template changes in `judaicalink-site` (also: show the changelog and the
  derived contributors on the dataset pages, 0013), restructuring the archive
  to `<slug>/<version>/<path>`, finder page `/dataindex/`.
- **To discuss with Frankfurt:** stable access URLs on data.judaicalink.org instead of web.judaicalink.org
  (0014); their loader expects `<slug>.meta.ttl` in one shared metadata graph (0006); their catalogue pages
  could link to our finder; they adopt `<slug>/<version>/<path>` when they next take over files.
- **Process details:** versioning and archiving rules for dumps.

- **Dumps clean start** ([0015](decisions/0015-dumps-clean-start.md)): the new tree is `lokal/dumps-new` (91 files,
  758 MB, `catalog.py collect`). To do: publish it on archive.judaicalink.org (replacing dumps-clean; redirects
  from the old paths?), then keep the backups 2025-02-06 and 2025-12-19 of `labs:/data/dumps` offline and
  delete the rest there.

## URI space and catalogue consistency

- **geo-coordinates** coins URIs without a namespace (`data/Aachen`, 2,701 places); no decision for this is
  known. Its places are typed only `skos:Concept`. `dbp-wiki-geo-linking` uses the same URIs. No other
  archived dataset links to them. Proposal: a successor with URIs in a proper namespace, typed `jl:Place`,
  linked to the old URIs.
- **Authority namespaces:** `data/gnd/`, `data/dbpedia/`, `data/geonames/` are not dataset namespaces but
  JudaicaLink URIs for entities of an authority, shared by several datasets (`data/dbpedia/` by
  `dbpedia-persons` and the Compact Memory entities of `cm-tagme`; `data/geonames/` by `geo-enriched` and
  `dbp-wiki-geo-linking`, without a dataset describing these places as records). Proposal: document this as
  a convention.
- **Catalogue inconsistencies:** epidat has `dataslug`/`graph` `epi` but URIs `data/epidat/`; no `dataslug` for
  yivo, rujen, rujen-translation, date-enriched, dbp-wiki-geo-linking; geo-coordinates `graph` is
  `data/geo-coor`; rujen contains one junk subject `mailto%3Amail%40rujen.ru`.

## Data

- **gba URIs changed** on 2025-03-21 ("Sanitize ids"): the 24 URIs of the version before are gone (e.g.
  `data/gba/JecheskelEzechielLandau`). Check whether anything links to the old ones.
- **Ontology:** the catalogue now names version 2025-11-27 (judaicalink-ontology `b26c961`, identical to
  ontology.judaicalink.org), in `lokal/dumps-additions/ontology/2025-11-27/`, not yet published. To do: rebuild
  `ontology-complements`, which redefines six terms of the current ontology (`belongsToIssue`,
  `belongsToJournal`, `birthLocationURI`, `deathLocationURI`, `gitCommit`, `gitWeb`), and load it in QLever.

- **YIVO articles are untyped:** the 1,798 articles have no `rdf:type`, so they are on no entity page; the 346
  article subsections (`skos:Concept`) were taken as subjects. Proposal: a typing dataset (`record-classes`):
  life dates at the start of the abstract → person (1,077), place links → place, else subject; subsections
  are not subjects; records keep their place on continued pages even without a type.
- **GeoNames nodes** (803) and a few haskala/djh records without type: check what they are before typing.
- **Typing for geo-coordinates** (`jl:Place`), see above.
- Further items of the data improvement plan: `../PLAN-2026-10-05-data-improvements.md`.

## Other threads

- Compact Memory full-text index for the portal (handover to Frankfurt): `../NOTES-2026-10-05-cm-fulltext-portal.md`.
- **Entity pages and the catalogue:** how entity-page sets fit the catalogue model (one dataset per run as
  now, or versions of one dataset); own documentation and discussion.
- Entity-page demonstrator: deployment files exist (`../ep-demonstrator/deploy/`), to be adapted to
  mannheim.judaicalink.org instead of `judaicalink.ki.hs-mannheim.de`.
