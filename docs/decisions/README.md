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
| [0005](0005-dumps-archive-and-mannheim.md) | Dumps: archive.judaicalink.org for preservation, mannheim.judaicalink.org/dumps for newer versions | 2026-10-07 |
| [0006](0006-graphs-and-meta.md) | One file = one named graph = dataset IRI; `-meta` files with provenance | 2026-10-05 |
| [0007](0007-complementary-and-superseding-datasets.md) | Prefer complementary datasets; fix by superseding, never by editing published dumps | 2026-10-05 |
| [0008](0008-facts-about-records.md) | Facts are stated about records and about the entity they concern | 2026-10-06 |
| [0009](0009-entity-pages.md) | Entity pages: one set at a time, core classes, precedence, IRI lifecycle | 2026-10-06 |
| [0010](0010-nli-exception.md) | Exception: legacy NLI entity pages are not carried over | 2026-10-06 |
| [0011](0011-reproducible-generation.md) | Generators are deterministic and independent of their earlier output | 2026-10-06 |
| [0012](0012-language.md) | Everything in English | 2026-10-07 |
| [0013](0013-catalogue-format.md) | Catalogue entry format: datasets, versions (stable pointer), changelog; only slug, title, author, license required | 2026-10-08 |
| [0014](0014-locations-dataindex-finder.md) | Locations only as prefixes; `dataindex.json` and the dataset finder; entries reach catalogues by copying | 2026-10-08 |
| [0015](0015-dumps-clean-start.md) | Clean start of the dumps: dumps-clean versions plus richer earlier ones (stable), single files, built by checksum | 2026-10-09 |
| [0016](0016-data-access-outside.md) | SPARQL endpoint, demonstrators and data access are not part of judaicalink-data | 2026-10-10 |
