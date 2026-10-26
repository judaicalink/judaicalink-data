# 0038 The facts of an entity page per class

Status: accepted · Date: 2026-10-26 · Amends [0022](0022-entity-pages-in-the-framework.md), [0029](0029-identity-from-our-linksets.md)

## Context

The entity pages state names, descriptions, coordinates and identifiers for every class, but dates, places and the
other facts only for persons. A work showed its title and nothing else, although its records give its authors,
date, place of publication and language. A survey of the members of ep 2026-10-26 (the properties of the records of
each class, per dataset) shows which facts the sources give for works, organisations, places and subjects.

## Decision

- **The rule of persons for every class:** a fact comes from the first record, in the record order of the group
  (dataset precedence, then the order among the records of one dataset), that has it. A text and its normalised
  value, or a text and its IRI, come from the same record. A fact with several values (creators, languages,
  publishers, seats, broader subjects) takes all values of that one record, not the union of the records, which would
  mix the facts of records joined by mistake. IRIs are kept as the source gives them (a record or an authority
  identifier); the views show their labels.
- **Works:** `dcterms:creator` (gnd `firstAuthor`, `dcterms:creator`, `gndo:author`), `dcterms:issued` and
  `jl:issuedNormalized` (gnd `dateOfPublication`/`dateOfProduction`, `dcterms:issued`, `dcterms:date`, lc
  `creationDateStart`, haskala `gregorian_year`; footprints `publicationDate` as the normalised value),
  `jl:placeOfPublication` and `jl:placeOfPublicationURI` (haskala `publication_place`, footprints `place`),
  `dcterms:language` (gnd `languageCode`, haskala, footprints), `dcterms:publisher` (footprints, haskala).
- **Organisations:** `gndo:dateOfEstablishment` and `gndo:dateOfTermination` (gnd, hhkeydocs, lc
  `activityStartDate`/`activityEndDate`; only values with a year) with `jl:establishmentDateNormalized` and
  `jl:terminationDateNormalized`; `gndo:placeOfBusiness` (gnd).
- **Places:** coordinates as before. **Subjects:** `skos:broader` (yivo).
- **Descriptions** also from the GND's `biographicalOrHistoricalInformation` (all classes; 40 characters or more, as
  the other descriptions).
- **Normalised dates** by `jl.dates` (0035): the normalised value of the same record, else a year, year and month or
  day of the text (also "30.10.1998"), else the first normalised value of the group; EDTF where the value is no single
  day, month or year (the person dates of ep 2026-10-26 typed 139 EDTF values as `xsd:gYear`).
- The platform view shows these facts per class, like the facts of persons.
- New terms of the ontology: `jl:issuedNormalized`, `jl:placeOfPublicationURI`, `jl:establishmentDateNormalized`,
  `jl:terminationDateNormalized` (pull request to judaicalink-ontology).
