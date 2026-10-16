# Open issues

State 2026-10-12. Remove an item when it is solved (with a reference to the decision or commit).

## Setting up

- **Generator framework** ([0018](decisions/0018-generator-framework.md), accepted 2026-10-12): built (`jl`, steps
  1–5 of 2026-10-11): generators, runs, versions, `-meta`, imports, agents and vocabulary; every catalogue version
  has an import record and a `-meta`. Not built yet: checking `requirements.txt` of acquisition steps.
- **Move the generators** (`../kg-complements/`) into this repository as framework generators: groupings, ontology
  pull requests and order in [0020](decisions/0020-kg-complements-into-the-framework.md); all done 2026-10-12, the
  entity pages as `ep` 2026-10-12 ([0022](decisions/0022-entity-pages-in-the-framework.md)); the entity-page pull
  request is prepared (branch `entity-page-terms`). `../ep-demonstrator` and `../dashboard` still read
  `ep-2026-10-06` (now in `lokal/work/superseded/`) and `jl:occupationConcept`: to switch to `ep` 2026-10-12 and
  `jl:occupationURI`; `jl:curationStatus` and `jl:supportedBy` are no longer stated (derived); the demonstrator reads the presence figures as
  `jl:cmMentionCount` etc. on the entity from the graph `cm-entities-presence`: now `jl:CorpusPresence` nodes in
  `cm-entities` (0020). Create the GitHub repository.
- **Catalogue:** 33 entries in the format of [0013](decisions/0013-catalogue-format.md) (migrated 2026-10-09;
  `kind` and `method` for all, 2026-10-12). Next: the remaining hand curation (`namespaces` checked against the
  data, `occupations`, file descriptions, HTML left in older bodies), entries for our new datasets, then adapting
  judaicalink-site (templates, finder, `dumpLocations`) and handing the catalogue and its documentation to
  Frankfurt.
- **Fuseki warnings** (test load of all stable versions into Fuseki 6.2.0, 2026-10-13: 20.6 million triples, 81 graphs,
  every graph equal to the `void:triples` of its `-meta` less the 85 corrections): 13 impossible dates typed
  `xsd:date` (e.g. `1902-02-29`, `1971-04-31`; 7 in records-normalized, 6 carried into ep), which records-normalized
  should not type as dates; 57 IRIs with `[` or other characters not allowed in IRIs, all legacy `data/nli/` URIs (47 in
  ls-nli-legacy, 1 in date-enriched). Jena loads both with a warning.
- **Catalogue, open questions** (0013): when to remove the old `archive.judaicalink.org/dumps/` (0027), and whether
  its paths then redirect (a `current` symlink per dataset makes 34 of the 82 old paths resolve again, 0018); DOIs for versions (would need a location that promises permanence, e.g. Zenodo; 0019).
- **Licence evidence** (0013, 2026-10-15): for every dataset we must be able to show why its licence holds. Where the
  source states it publicly: `license.statement`, an archived capture of that page (done for footprints). Where we
  have a written permission: the document. yivo, rujen and djh are CC0 by written permission (yivo and djh publish
  only the beginning of each article), but the permissions exist only on paper. To do: scan them, keep the files
  privately (not in git), and record in the catalogue only a file name and its SHA-256, so the document can be
  found quickly (field still to define in 0013). Then check every other entry whose licence the source does not
  state publicly (e.g. hhkeydocs, stolpersteine, haskala, sosy, jre, hirsch-family, ubffm-persons).
  hhkeydocs: its terms of use (schluesseldokumente.net/nutzungsbedingungen, archived 2026-10-11) put the articles
  and source interpretations under CC BY-NC-ND 4.0, but say nothing about the index of persons, places and
  organisations that the dataset holds; to ask the IGdJ.
- **mannheim.judaicalink.org:** the platform and its decisions are in `../judaicalink-mannheim/` (`docs/decisions/`,
  not on GitHub yet); a local test VM runs it. Engine comparison (QLever, Fuseki) in `../endpoints/`.
- **Ontology (found 2026-10-14, with decision 0002 of judaicalink-mannheim):** rujen uses `jl:Person` as a class (8,283 records), which the ontology does not
  define (it has `jl:Place`): add the term or map rujen to another class. In Frankfurt, ontology term IRIs do not resolve
  (`data.judaicalink.org/ontology/<term>` → a 404 page of the portal, also for Turtle); suggest a redirect to
  ontology.judaicalink.org.
- **Catalogue tools and finder** ([0014](decisions/0014-locations-dataindex-finder.md)): `jl
  update-dataindex|sync-site`, the finder page and template changes in `judaicalink-site` (also: show the changelog and the
  derived contributors on the dataset pages, 0013), restructuring the archive
  to `<slug>/<version>/<path>`, finder page `/dataindex/`.
- **The five removed datasets** (0015; confirmed 2026-10-12): their pages in `judaicalink-site/content/datasets/` are
  deleted by hand when the site is synced (the sync never removes entries, 0014). `/datasets/ep-supp/`,
  `/datasets/cm-tagme-supp/` and `/datasets/rujen-translation-supp/` redirect to `ep`, `cm-tagme` and
  `rujen-translation` (aliases); `cmtest` and `beacon-persons` have no related page. (`rujen-translation` claimed the two old
  encyclopedia URLs of `rujen` as well, also on the site; removed 2026-10-12, they redirect to `rujen`.)
- **To discuss with Frankfurt:** they can drop `cmtest`, `ep-supp`, `cm-tagme-supp`, `rujen-translation-supp` and
  `beacon-persons` from their catalogue ([0015](decisions/0015-dumps-clean-start.md)); stable access URLs on data.judaicalink.org instead of web.judaicalink.org
  (0014); their loader expects `<slug>.meta.ttl` in one shared metadata graph (0006); their catalogue pages
  could link to our finder; they adopt `<slug>/<version>/<path>` when they next take over files; their named graphs `data/<x>` become the dataset IRIs `datasets/<slug>` when they load our catalogue state (the catalogue no longer names the old graphs, 0018). Also: their
  catalogue has the `https` examples fixed in ours (hhkeydocs, sosy, ontology) and the entry `stolperstein.md`
  (now `stolpersteine`, [0017](decisions/0017-slug-stolpersteine.md)); their pubby takes the graph from
  `dataslug` (sometimes a namespace, e.g. `epi`); the BEACON `#TARGET` is `https://data.judaicalink.org/data/gnd/{ID}`
  (`generate_beacon.py` default), so DNB EntityFacts spreads our URIs in the `https` form: ask for `http://`.
- **Process details:** which versions each dumps location offers; when to prune historical versions (0019).
- **The store and the inputs area** (0019, [0021](decisions/0021-store-and-inputs-area.md)): where they live (now
  `lokal/` on Kai's machine; later the platform VM?) and their backup. Inputs still outside the inputs area: the web
  caches (`lokal/work/api-cache`), the NLI export, the other inputs of kg-complements (moved when their datasets are
  ported, 0020), and what the labs VM backup holds (`../BACKUP-PLAN-2026-10-10.md`).

- **Dumps clean start** ([0015](decisions/0015-dumps-clean-start.md)): the new tree is the store `lokal/store` (formerly `dumps-new`; 179 files,
  318 MB, `jl collect-store`), published 2026-10-13 on archive.judaicalink.org/store/ (beside the old `/dumps/`, 0027). To do: remove the old
  `/dumps/` there some day; keep the backups 2025-02-06 and 2025-12-19 of `labs:/data/dumps` offline and
  delete the rest there. Nothing else on the VM is deleted before the backup in
  `../BACKUP-PLAN-2026-10-10.md` exists (`/data/archive`, `/data/cm` and more hold the only copies of sources,
  intermediates and working folders).

## URI space and catalogue consistency

- **URI check of 2026-10-10** (all files of `dumps-new`, now `store`, and `dumps-additions`): URIs are consistently `http://`,
  datasets are identified only as `http://data.judaicalink.org/datasets/<slug>`. To fix:
  - 953 `owl:sameAs` to `https://data.judaicalink.org/data/gnd/…` in `gnd-persons-entityfacts` and `ep-2026-10-06`,
    taken from the EntityFacts `sameAs` (from the BEACON target, see Frankfurt): normalise to `http` when regenerating
    (they become self-links and are dropped). Done for `gnd-persons-entityfacts` 2026-10-12 (950 dropped, 3 kept as
    `http`); `ep` 2026-10-12 has none.
  - The `-meta` files in `dumps-additions` use patterns that the generator framework replaces: access URLs in the old
    archive layout, `datasets/agent/…` with names in the IRIs (→ `datasets/agents/persons/<id>`, `datasets/agents/software/<name>`;
    names only in an agents dataset, so a name can be removed without new IRIs; slug `agents` reserved), `datasets/<slug>/generation/<date>`,
    `datasets/<slug>-meta/creator/…`, `…/original-generation`, `https` examples copied from the catalogue (fixed in the
    catalogue 2026-10-10). Regenerate all with the framework. Done 2026-10-11 for the catalogue versions (`jl
    render-meta --all`, in the store); still to do for the datasets of `dumps-additions` when they come into the
    framework, and the new `-meta` files are not at any dumps location yet.
  - Graph of the `-meta` files: `datasets/<slug>-meta` → `datasets/<slug>/meta` (0018) in `../qlever/make_inputs.py`
    (graph from the file name) and in the kg-complements `-meta` writer.
  - The legacy ep of 2021 has three entity pages `owl:sameAs` a dataset IRI (yivo, rujen, rujen-translation); `ep`
    2026-10-12 retires them (they have no record).
  - Still on the slug `stolperstein` (0017), because they read Frankfurt's catalogue: the graph in
    `../qlever/queries/07-stolpersteine-persons.rq`, the precedence list in `../kg-complements/ep_generator.py`, the
    dataset list in `../ep-demonstrator/app.py`, and the old `-meta` `dumps-additions/stolpersteine/current/stolperstein-meta.ttl.gz`.
    Change them when `make_inputs.py` and the generators switch to this catalogue (then rebuild the index).

- **geo-coordinates** coined URIs without a namespace (`data/Aachen`, 2,701 places), typed only `skos:Concept`.
  Fixed by geo-coordinates 2026-10-12: `data/geo-coordinates/<name>`, `jl:Place`, the old URIs `dcterms:isReplacedBy`
  the new ones (`dbp-wiki-geo-linking` still links the old URIs, valid through the replacement).
- **Authority namespaces:** `data/gnd/`, `data/dbpedia/`, `data/geonames/` are not dataset namespaces but
  JudaicaLink URIs for entities of an authority, shared by several datasets (`data/dbpedia/` by
  `dbpedia-persons` and the Compact Memory entities of `cm-tagme`; `data/geonames/` by `geo-enriched` and
  `dbp-wiki-geo-linking`, without a dataset describing these places as records). Proposal: document this as
  a convention.
- **Catalogue inconsistencies:** epidat had `dataslug`/`graph` `epi` but URIs `data/epidat/` (namespace corrected
  with epidat 2026-10-12); no `dataslug` for
  yivo, rujen, rujen-translation, date-enriched, dbp-wiki-geo-linking; geo-coordinates `graph` is
  `data/geo-coor`; rujen contains one junk subject `mailto%3Amail%40rujen.ru`.
  The `-meta` of epidat 2023-07-14, rendered again, would get the namespace `data/epidat/` and example of the entry,
  which fit only 2026-10-12 (the old version uses `data/epi/`); found 2026-10-15, not rendered.

## Data

- **footprints 2024-03-18 dates:** some `jl:birthDate`/`jl:deathDate` values are Python dictionaries written as text,
  e.g. `{'id': 996, 'edtf_format': '1663/1711', 'display': '1663 - 1711'}`; records-normalized leaves them out (found
  2026-10-12). The usable value is `edtf_format` (EDTF); a fix belongs to a new footprints version or a rule in
  records-normalized. records-normalized reads the EDTF value (2026-10-12); 20 are intervals or centuries and stay
  out (quality-annotations).
  Fixed in footprints 2026-10-12 (the dictionary dates repeat values of the person loop; dropped).
- **gba URIs changed** on 2025-03-21 (generator commit `6fce1cd`, `clean_url_string` replaces characters with `_`
  instead of removing them): the 24 URIs of the version before are gone (e.g. `data/gba/JecheskelEzechielLandau` →
  `Jecheskel__Ezechiel__Landau`). Check whether anything links to the old ones.
- **Findings of the generator inventory** (`generators/*/README.md`): yivo 2020 lower-cased its IRIs, so the yivo
  links of 2014links and `interlinks.n3` (2014 IRIs) do not resolve; epidat had names clipped by a hand repair of
  2023 (`Jakob` → `Jako`; epidat 2026-10-12 is made again from the source); rujen-translation contains 293 broken literals `"Translated(src=…)"`; sosy uses HTML-view
  URLs as `jl:occupation` values (204, `https://data.judaicalink.org/data/html/occupation/…`); the legacy entity pages made about 1.1 million cm-tagme references and
  compact-memory pages into singleton pages (`ep` 2026-10-12 retires them); djh 2018 has non-ASCII
  characters in IRIs; geo-enriched has an empty haskala file.
- **Ontology:** the catalogue now names version 2025-11-27 (judaicalink-ontology `b26c961`, identical to
  ontology.judaicalink.org), in `lokal/dumps-additions/ontology/2025-11-27/`, not yet published. To do: rebuild
  `ontology-complements`, which redefines six terms of the current ontology (`belongsToIssue`,
  `belongsToJournal`, `birthLocationURI`, `deathLocationURI`, `gitCommit`, `gitWeb`), and load it in an endpoint (with the platform, 0016).

- **Identity links, found with the entity-page closure (2026-10-12, decisions 0022–0024):** fixed by new versions of
  bhr and 2014links (links of rujen persons to places), template links dropped in gnd-persons-entityfacts, 76 wrong
  links in `corrections-links`. Still open: hhkeydocs had two persons linked to the GND number of a namesake (Otto
  Warburg, Kurt Singer), so its GND links may have been made by name; check them against the life dates.
  cm-entities takes all VIAF numbers of a Wikidata item, which can include a work's (Sahula). The closure check only
  sees conflations that meet a second Wikidata item or class; others need other checks (life dates of the records of
  a group). Havilah (dbpedia-persons, a person, and cm-entities, a place, with one Wikidata item for both) is left as
  it is.
- **sosy occupations:** 204 `jl:occupation` values are addresses of HTML views
  (`https://data.judaicalink.org/data/html/occupation/…`), which records-normalized restates as `jl:occupationURI`;
  a new sosy version should give the occupation IRIs.
- **epidat: place of burial as place of death.** Epidat gives the place of burial; epidat (2023 and 2026-10-12)
  states it as `jl:deathLocation`/`jl:deathLocationURI`, which is not true for everyone (decided 2026-10-12 to keep
  it). Proper terms (`jl:burialLocation`, `jl:burialLocationURI`) would need an ontology pull request and readers in
  records-normalized and ep. Also open for epidat: the family relations of the TEI (14,264, no ontology terms), the
  451 persons of 2023 that Epidat has withdrawn (seven cemeteries, "not yet published"; taken over again when Epidat
  publishes them), the cemetery GND/coordinates.
- **YIVO articles were untyped:** typed by record-classes 2026-10-12 and linked to Wikidata by ls-yivo-wikidata
  (decision 0025). Open: the 346 article subsections (`skos:Concept`), which ep takes as subjects; ep must read both
  datasets (classes from record-classes, `jl:Subject`).
- **GeoNames nodes** (803) and a few haskala/djh records without type: check what they are before typing.
- Further items of the data improvement plan: `../PLAN-2026-10-05-data-improvements.md`.

## Other threads

- Compact Memory full-text index for the portal (handover to Frankfurt): `../NOTES-2026-10-05-cm-fulltext-portal.md`.
- Entity-page demonstrator: deployment files exist (`../ep-demonstrator/deploy/`), to be adapted to
  mannheim.judaicalink.org instead of `judaicalink.ki.hs-mannheim.de`.

## Issues found from browsing the data, Kai 2026-10-15

- **Deprecated GNDs and https URIs in GND**
  Our data often shows multiple GND numbers, e.g.: http://data.judaicalink.org/data/ep/1000232
  The GND Identifier come from multiple sources where they are linkes as owl:sameAs. 
  In GND, all but one are deprecated and redirected to:
  <https://d-nb.info/gnd/4028586-8> gndo:gndIdentifier "4028586-8";
  owl:sameAs <http://viaf.org/viaf/23147121724526391653>, <http://www.wikidata.org/entity/Q1218>;
  gndo:oldAuthorityNumber "(DE-588)5210156-3";
  owl:sameAs <https://d-nb.info/gnd/5210156-3>;
  dnbt:deprecatedUri "https://d-nb.info/gnd/5210156-3";
  gndo:oldAuthorityNumber "(DE-588b)5210156-3", "(DE-588)5210124-1";
  owl:sameAs <https://d-nb.info/gnd/5210124-1>;
  dnbt:deprecatedUri "https://d-nb.info/gnd/5210124-1";
  gndo:oldAuthorityNumber "(DE-588b)5210124-1", "(DE-588)1028326-2";
  owl:sameAs <https://d-nb.info/gnd/1028326-2>;
  dnbt:deprecatedUri "https://d-nb.info/gnd/1028326-2";
  gndo:oldAuthorityNumber "(DE-588b)1028326-2", "(DE-588c)4028586-8";
  gndo:relatedDdcWithDegreeOfDeterminacy4 <http://dewey.info/class/2--569442/>;
  gndo:relatedDdcWithDegreeOfDeterminacy3 <http://dewey.info/class/2--33442/>;
  owl:sameAs <https://sws.geonames.org/281184>;
  geo:hasGeometry _:node1k0rmm5k0x239553038 .
  Thoughts: Is it helpful to have the deprecated URIs to merge data when we get external links with old identifiers?
  Instead of adding all of them, it would be better to collect them at our GND representaion in the gnd dataset.
  Could be done via a complementary dataset that adds all deprecated and sameAs URIs. Could be turned into a central
  service, where all kind=deprecated datasets are loaded and a lookup service is provided to return the current identifier. 
  Generators should always check foreign URIs against this service. The kind=deprecated datasets would be new datasets
  that are specifically created for important link sources like GND. Would contain ALL deprecated URIs, not JudaicaLink specific
  so that we can resolve all unknown new links.
  Alternative, generally usable, but slow: online dereferencing and looking for information if a URI should be updated.
- **GND uses https URIs, we link http URIs.** Fix all generators. The links might come from a source, should we centralize 
  this as as a cleanup or check task that is automatically run after a generation and looks for certain known issues like these?
- **Wrong GeoNames URIs** GeoNames has a slash at the end of its URIs and also uses https: https://sws.geonames.org/3247449/about.rdf
  Similar to GND. At least for prominent link targets, we need to document the correct URI schema and check all generated data. In this
  case the new geo-coordinates dataset did it wrong: http://data.judaicalink.org/data/geo-coordinates/Jerusalem
- 
