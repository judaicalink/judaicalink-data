# Decisions

One file per decision, numbered in order. A decision is changed by a new record that supersedes the old
one (the old one stays, with `Status: superseded by NNNN`). Each record: status, date, context, decision,
consequences. Short is better than complete; link to the documentation that has the details.

| No. | Decision | Date |
|---|---|---|
| [0001](0001-roles-and-hosts.md) | Roles: Frankfurt runs, Mannheim develops; mannheim.judaicalink.org as the Mannheim platform | 2026-10-07 |
| [0002](0002-uris.md) | We keep coining data.judaicalink.org URIs; demonstrators rewrite them | 2026-10-07 |
| [0003](0003-judaicalink-data-repository.md) | One universal repository `judaicalink-data` for generation, catalogue and decisions | 2026-10-07 |
| [0004](0004-complete-catalogue.md) | Our catalogue is complete, with changelog and the version identical to Frankfurt | 2026-10-07 |
| [0005](0005-dumps-archive-and-mannheim.md) | ~~Dumps: archive.judaicalink.org for preservation, mannheim.judaicalink.org/dumps for newer versions~~ (superseded by 0019) | 2026-10-07 |
| [0006](0006-graphs-and-meta.md) | One file = one named graph = dataset IRI; `-meta` files with provenance | 2026-10-05 |
| [0007](0007-complementary-and-superseding-datasets.md) | Prefer complementary datasets; fix by superseding, never by editing published dumps | 2026-10-05 |
| [0008](0008-facts-about-records.md) | Facts are stated about records and about the entity they concern | 2026-10-06 |
| [0009](0009-entity-pages.md) | Entity pages: one set at a time, core classes, precedence, IRI lifecycle (amended by 0022) | 2026-10-06 |
| [0010](0010-nli-exception.md) | ~~Exception: legacy NLI entity pages are not carried over~~ (superseded by 0022) | 2026-10-06 |
| [0011](0011-reproducible-generation.md) | Generators are deterministic and independent of their earlier output | 2026-10-06 |
| [0012](0012-language.md) | Everything in English | 2026-10-07 |
| [0013](0013-catalogue-format.md) | Catalogue entry format: datasets, versions (stable pointer), changelog; only slug, title, author, license required | 2026-10-08 |
| [0014](0014-locations-dataindex-finder.md) | Locations only as prefixes; `dataindex.json` and the dataset finder; entries reach catalogues by copying | 2026-10-08 |
| [0015](0015-dumps-clean-start.md) | Clean start of the dumps: dumps-clean versions plus richer earlier ones (stable), single files, built by checksum | 2026-10-09 |
| [0016](0016-data-access-outside.md) | SPARQL endpoint, demonstrators and data access are not part of judaicalink-data | 2026-10-10 |
| [0017](0017-slug-stolpersteine.md) | Slugs name the dataset (namespace chosen separately); `stolperstein` renamed to `stolpersteine` | 2026-10-10 |
| [0018](0018-generator-framework.md) | Generator framework (accepted 2026-10-12) | 2026-10-10 |
| [0019](0019-dumps-locations-equal.md) | Dumps locations are equal, none permanent; files of a version never change; the git history is the permanent record; pruning possible; public dumps lean, the rest in the store (amended by 0021) | 2026-10-11 |
| [0020](0020-kg-complements-into-the-framework.md) | The kg-complements datasets in the framework: groupings (15 → 7 datasets and a new compact-memory version), ontology terms as pull requests to judaicalink-ontology, `jl:occupationURI`, order | 2026-10-12 |
| [0021](0021-store-and-inputs-area.md) | The store is the dumps (only published files); inputs that are not published live in an inputs area `<source>/<name>/` with `input.toml` | 2026-10-12 |
| [0022](0022-entity-pages-in-the-framework.md) | Entity pages: sets are versions of `ep`; groups by a fresh closure of identity links (same key joins, no guards); merges (`jl:mergedInto`, oldest IRI kept) and splits by comparison with the previous set; deprecated record IRIs as closure nodes; no NLI exception | 2026-10-12 |
| [0023](0023-correction-datasets.md) | Correction datasets (kind `correction`): additions as data, deletions as SPARQL Update (`-deletions.ru.gz`), applied after all other datasets | 2026-10-12 |
| [0024](0024-which-fix-for-which-error.md) | Which fix for which error: a systematic error of one dataset → a new version of it (fixes as parameters); single findings → correction datasets; new facts → complements | 2026-10-12 |
| [0025](0025-record-classes-and-wikidata-links.md) | Classes of untyped records in a complement `record-classes` (automated; first the yivo articles, by their Wikidata class or life dates); yivo articles linked to Wikidata in the linkset `ls-yivo-wikidata` | 2026-10-12 |
| [0026](0026-haskala-from-the-database.md) | haskala made from the Drupal database of 2015, true to the database (all nodes, fields, terms and the schema; terms in `data/haskala/vocab/`, IRIs from the database keys); 2019 IRIs replaced, their GND links carried over | 2026-10-13 |
| [0027](0027-store-beside-the-old-dumps.md) | The store is published in `archive.judaicalink.org/store/`, beside the old `/dumps/`, which stays for now | 2026-10-13 |
| [0028](0028-user-agent.md) | One User-Agent `JudaicaLink-data (https://judaicalink.org)` for every request (`jl.fetch`); overrides by the generator or per host in `local.toml` (proposed) | 2026-10-15 |
| [0029](0029-identity-from-our-linksets.md) | Identity on the entity pages only from our linksets (by key, with rules); external sources (Wikidata, VIAF, LC, GeoNames, GND, DBpedia) kept on file as datasets, trusted and described; VIAF linked unless dates contradict (proposed) | 2026-10-16 |
| [0030](0030-dcterms-only.md) | Dublin Core: only `dcterms:`, also where a source uses the elements; a run that writes `dc:` fails | 2026-10-18 |
| [0031](0031-wikipedia-dbpedia-per-language.md) | Wikipedia and DBpedia are one source per language; one dataset `dbpedia` with `data/dbpedia/en/`, `data/dbpedia/de/`; other languages only as links | 2026-10-18 |
| [0032](0032-identity-declarations.md) | Identity declared per dataset in the catalogue (`identity`); link quality measured per dataset and property, a threshold for joining; identifier patterns, hub check, one record per dataset (proposed) | 2026-10-18 |
| [0033](0033-withdrawn-datasets.md) | A dataset with `withdrawn` is left out of the stable inputs, the cascade, the entity pages and the loaders; its versions stay; 2014links withdrawn | 2026-10-19 |
| [0034](0034-footprints-from-the-api.md) | footprints made from the Footprints API, true to the API (four levels, terms in `data/footprints/vocab/`, IRIs from the API ids); persons classed in `record-classes`; the 2024 IRIs replaced by the records they stood for (several: a split) | 2026-10-25 |
| [0035](0035-dates-edtf.md) | Normalised dates: `xsd:date`/`gYearMonth`/`gYear` where the value fits, else EDTF (LC datatype); a source's normalised form is stated by the record dataset | 2026-10-25 |
| [0036](0036-several-places-through-geonames.md) | Places joined through GeoNames may hold several records of one dataset (city and administrative unit); other unions keep one record per dataset | 2026-10-26 |
| [0037](0037-judged-linksets.md) | Links of a unit below the threshold may be judged one by one (rules, then an LLM); the correct ones form a linkset of their own (methods `rule-based`, `llm-judged`), which joins | 2026-10-26 |
| [0038](0038-facts-per-class.md) | The facts of an entity page per class (works, organisations, subjects), chosen as for persons: first record by precedence, values that belong together from one record | 2026-10-26 |
| [0039](0039-occupations-in-one-dataset.md) | Occupations are the GND's subject headings: `gnd` links them (`jl:occupationURI`), the dataset `occupations` describes them and the older `data/occupation/` IRIs (linked to them); no IRIs of our own, no entity pages | 2026-10-31 |
| [0040](0040-pictures-of-entries.md) | Pictures of entries are files of the catalogue (`catalog/pictures/<slug>/`); `picture` is a path relative to `catalog/`; the sites copy them with the entries | 2026-10-31 |
| [0041](0041-pruning.md) | Pruning: per dataset the oldest, the newest and one version per month stay public (and the stable version and pinned inputs); a pruned version stays in the catalogue (`pruned`), its files move to the private pruned area | 2026-10-31 |
