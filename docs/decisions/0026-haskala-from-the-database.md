# 0026 haskala from the Drupal database, true to the database

Status: accepted · Date: 2026-10-13

## Context

The dataset `haskala` (2019, 2025) held 226 persons: 194 scraped from the person pages of haskala-library.net and
32 from a list of the University of Potsdam (haskala.net), with GND data added by hand. The site, now offline, was a
Drupal 7 front end to the database of a German-Israeli research project (2004-2010): 1,980 persons, 525 books with up
to 173 fields each, editions, mentions, productions, prefaces, translations and 19 taxonomies. Dumps of that database
are in the repository of the new Haskala portal ([judaicalink/haskala](https://github.com/judaicalink/haskala)); its
own RDF export is generated from the portal's Django models, with IRIs and terms of that implementation.

## Decision

- **Source:** the complete dump of 2015-04-20 (`research/haskala.sql`), the original of the reduced copies of 2023
  and 2024 with the same content. Only an allow-list of tables is kept in the inputs area
  (`inputs:haskala/drupal-2015-04-20`): content, schema, migration maps, search configuration; not the user accounts,
  sessions, logs, caches and settings (personal data, credentials). The user accounts carry no information about
  the content (all nodes were created by the migration account).
- **True to the database:** every node, field value and term is stated, and the schema too (content types, fields,
  types, cardinality, targets, allowed values, labels, help texts, order, visibility), so that the database can be
  rebuilt from the data without a particular portal. Left out: the one page of site text and the Drupal bookkeeping
  (timestamps of the migration, revisions, owner). Text in Drupal's HTML formats is `rdf:HTML` (the notes mark
  chronograms with `<strong>`/`<ins>`).
- **Terms in the dataset namespace:** the classes and properties of the database are coined in
  `data/haskala/vocab/` (machine names of Drupal without `field_`; classes capitalised) and defined in a file of the
  version, not in the JudaicaLink ontology: about 200 terms of one source. JudaicaLink and standard terms are stated
  in addition where they exist (persons, books, places, names, VIAF, dates, concepts).
- **IRIs from the database keys:** `data/haskala/<content type>/<node id>` and `data/haskala/<vocabulary>/<term id>`;
  the record ids of the research database (migration maps) as `dcterms:identifier`.
- **The 2019 IRIs:** the library persons are `dcterms:isReplacedBy` their nodes (matched by their page address); the
  GND links of 2019, which the database does not have, are carried over to the nodes in a file of their own. The
  haskala.net persons, a different source, keep their IRIs and 2019 data in a file of their own.
- **Licence CC BY 4.0** (decided 2026-10-13; it was CC0): crediting the authors of the Library of Haskala (with a
  link to the dataset description), the FID Jewish Studies and JudaicaLink (`attribution` of the licence, 0013).
  A change to CC0 stays possible later, the other way round not. The versions 2019-07-01 and 2025-03-24 were published
  under CC0 and stay available under it.
- **Not added:** direct person-book links (e.g. author) derived from the productions; the data keeps the model of the
  database. They can come in a complement later.

## Consequences

- `haskala` 2026-10-12 is made from the database (`generators/haskala/generate.py`); its persons, books and cities
  get entity pages, joined through VIAF and the carried-over GND links.
- The field groups (sections of the book page) and the views (browse and search pages) were defined in code and are
  not in any dump; a viewer that rebuilds the library needs its own layout. Where Drupal labels are ambiguous
  ("Notes"), the field instance says which content type the field belongs to, and the property label follows the
  machine name.
