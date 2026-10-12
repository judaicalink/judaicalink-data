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
