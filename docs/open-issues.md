# Open issues

State 2026-10-07. Remove an item when it is solved (with a reference to the decision or commit).

## Setting up

- **Generator tooling** (when the generators move here): generators coin version ids (default
  `YYYY-MM-DD[-n]`, other schemes per dataset possible); the tooling can add the version entry (files,
  sizes, checksums, commit) to the dataset's catalogue entry, **only on request**, so experimental runs are
  not catalogued.
- **Generators:** `generators/<slug>/` documents the history and holds the original files of every dataset (step 1,
  2026-10-10). Next: the generator framework, migrated generators (with a test against the kept version where the
  inputs are on file), then the new datasets.
- **Move the generators** (`../kg-complements/`) into this repository, change the provenance
  links in the `-meta` files (placeholder `judaicalink-generators/…/kg-complements/`) to `judaicalink-data`,
  create the GitHub repository.
- **Catalogue:** the entries in `catalog/` (31 since 0015) are migrated to the format of
  [0013](decisions/0013-catalogue-format.md) (2026-10-09, `catalog/migrate_0013.py`; `jl check-catalog`
  passes). Next: the hand curation (`kind`, `method`, `namespaces` checked
  against the data, `occupations`, file descriptions), restructuring the archive, entries for our
  new datasets, then adapting judaicalink-site (templates, finder, `dumpLocations`) and handing the catalogue
  and its documentation to Frankfurt.
- **Catalogue, open questions** (0013): redirects from the old archive paths (a `current` symlink per dataset
  makes 34 of the 82 old paths resolve again, 0018); DOIs for versions (would need a location that promises permanence, e.g. Zenodo; 0019).
- **mannheim.judaicalink.org:** reproducible setup (SPARQL endpoint, dumps, demonstrators), independent of
  the grown setup of the VM; where the platform code lives; whether a pubby-like frontend is needed.
  Which SPARQL engine: QLever changes literal values (0018), so engines are compared in `../endpoints/`
  (prepared 2026-10-11, QLever 0.6.0 measured; Oxigraph, Jena Fuseki, Virtuoso to be installed and run).
- **Catalogue tools and finder** ([0014](decisions/0014-locations-dataindex-finder.md)): `jl
  update-dataindex|sync-site`, the finder page and template changes in `judaicalink-site` (also: show the changelog and the
  derived contributors on the dataset pages, 0013), restructuring the archive
  to `<slug>/<version>/<path>`, finder page `/dataindex/`.
- **To discuss with Frankfurt:** they can drop `cmtest`, `ep-supp`, `cm-tagme-supp`, `rujen-translation-supp` and
  `beacon-persons` from their catalogue ([0015](decisions/0015-dumps-clean-start.md)); stable access URLs on data.judaicalink.org instead of web.judaicalink.org
  (0014); their loader expects `<slug>.meta.ttl` in one shared metadata graph (0006); their catalogue pages
  could link to our finder; they adopt `<slug>/<version>/<path>` when they next take over files. Also: their
  catalogue has the `https` examples fixed in ours (hhkeydocs, sosy, ontology) and the entry `stolperstein.md`
  (now `stolpersteine`, [0017](decisions/0017-slug-stolpersteine.md)); their pubby takes the graph from
  `dataslug` (sometimes a namespace, e.g. `epi`); the BEACON `#TARGET` is `https://data.judaicalink.org/data/gnd/{ID}`
  (`generate_beacon.py` default), so DNB EntityFacts spreads our URIs in the `https` form: ask for `http://`.
- **Process details:** which versions each dumps location offers; when to prune historical versions (0019).
- **The store** (0019): where it lives (now `lokal/` on Kai's machine; later the platform VM?), its backup, and
  moving into it what is kept today in `lokal/work`, `lokal/export` and the labs VM backup (`../BACKUP-PLAN-2026-10-10.md`).

- **Dumps clean start** ([0015](decisions/0015-dumps-clean-start.md)): the new tree is the store `lokal/store` (formerly `dumps-new`; 79 files,
  189 MB, `jl collect-store`). To do: publish it on archive.judaicalink.org (replacing dumps-clean; redirects
  from the old paths?), then keep the backups 2025-02-06 and 2025-12-19 of `labs:/data/dumps` offline and
  delete the rest there. Nothing else on the VM is deleted before the backup in
  `../BACKUP-PLAN-2026-10-10.md` exists (`/data/archive`, `/data/cm` and more hold the only copies of sources,
  intermediates and working folders).

## URI space and catalogue consistency

- **URI check of 2026-10-10** (all files of `dumps-new`, now `store`, and `dumps-additions`): URIs are consistently `http://`,
  datasets are identified only as `http://data.judaicalink.org/datasets/<slug>`. To fix:
  - 953 `owl:sameAs` to `https://data.judaicalink.org/data/gnd/…` in `gnd-persons-entityfacts` and `ep-2026-10-06`,
    taken from the EntityFacts `sameAs` (from the BEACON target, see Frankfurt): normalise to `http` when regenerating
    (they become self-links and are dropped).
  - The `-meta` files in `dumps-additions` use patterns that the generator framework replaces: access URLs in the old
    archive layout, `datasets/agent/…` with names in the IRIs (→ `datasets/agents/persons/<id>`, `datasets/agents/software/<name>`;
    names only in an agents dataset, so a name can be removed without new IRIs; slug `agents` reserved), `datasets/<slug>/generation/<date>`,
    `datasets/<slug>-meta/creator/…`, `…/original-generation`, `https` examples copied from the catalogue (fixed in the
    catalogue 2026-10-10). Regenerate all with the framework.
  - Graph of the `-meta` files: `datasets/<slug>-meta` → `datasets/<slug>/meta` (0018) in `../qlever/make_inputs.py`
    (graph from the file name) and in the kg-complements `-meta` writer.
  - The legacy ep of 2021 has three entity pages `owl:sameAs` a dataset IRI (yivo, rujen, rujen-translation); not
    carried over into ep-2026-10-06 (checked).
  - Still on the slug `stolperstein` (0017), because they read Frankfurt's catalogue: the graph in
    `../qlever/queries/07-stolpersteine-persons.rq`, the precedence list in `../kg-complements/ep_generator.py`, the
    dataset list in `../ep-demonstrator/app.py`, and the old `-meta` `dumps-additions/stolpersteine/current/stolperstein-meta.ttl.gz`.
    Change them when `make_inputs.py` and the generators switch to this catalogue (then rebuild the index).

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

- **gba URIs changed** on 2025-03-21 (generator commit `6fce1cd`, `clean_url_string` replaces characters with `_`
  instead of removing them): the 24 URIs of the version before are gone (e.g. `data/gba/JecheskelEzechielLandau` →
  `Jecheskel__Ezechiel__Landau`). Check whether anything links to the old ones.
- **Findings of the generator inventory** (`generators/*/README.md`): yivo 2020 lower-cased its IRIs, so the yivo
  links of 2014links and `interlinks.n3` (2014 IRIs) do not resolve; epidat has names clipped by a hand repair of
  2023 (`Jakob` → `Jako`); rujen-translation contains 293 broken literals `"Translated(src=…)"`; sosy uses HTML-view
  URLs as `jl:occupation` values (204, `https://data.judaicalink.org/data/html/occupation/…`); the legacy entity pages made about 1.1 million cm-tagme references and
  compact-memory pages into singleton pages (check that ep-2026-10-06 retires them); djh 2018 has non-ASCII
  characters in IRIs; geo-enriched has an empty haskala file.
- **Ontology:** the catalogue now names version 2025-11-27 (judaicalink-ontology `b26c961`, identical to
  ontology.judaicalink.org), in `lokal/dumps-additions/ontology/2025-11-27/`, not yet published. To do: rebuild
  `ontology-complements`, which redefines six terms of the current ontology (`belongsToIssue`,
  `belongsToJournal`, `birthLocationURI`, `deathLocationURI`, `gitCommit`, `gitWeb`), and load it in an endpoint (with the platform, 0016).

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
