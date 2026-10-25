# 0035 Normalised dates: XSD where the value fits, else EDTF

Status: accepted · Date: 2026-10-25

## Context

Dates are stated as the source writes them (`jl:birthDate`, `dcterms:date`, `dcterms:issued`: text); the normalised
value is typed (`jl:birthDateNormalized`: `xsd:date`, `xsd:gYearMonth`, `xsd:gYear`), derived by records-normalized
(0020). Many dates of the sources are not one day, month or year: intervals ("1663/1711"), approximate or uncertain
dates ("c. 1778"), decades ("182X"). XSD cannot express them, so records-normalized leaves them without a normalised
value. Footprints writes every date in the Extended Date/Time Format (EDTF, ISO 8601-2), which expresses them.

## Decision

- A normalised date is `xsd:date`, `xsd:gYearMonth` or `xsd:gYear` where the value is one day, month or year (EDTF
  level 0 without qualification), else the EDTF value typed `http://id.loc.gov/datatypes/edtf/EDTF` (the datatype of
  the Library of Congress for EDTF).
- Where a source gives a normalised form (Footprints: EDTF), the record dataset states it, converted by this rule; the
  text stays as the source displays it. Persons: `jl:birthDate`/`jl:deathDate` (text) and
  `jl:birthDateNormalized`/`jl:deathDateNormalized`. Other dates: the text in the common term (`dcterms:issued`,
  `dcterms:date`), the normalised value in the property of the dataset's vocabulary for that field.
- records-normalized adds no normalised date to a record that has one.

## Consequences

- records-normalized can write EDTF where it reads an interval, an approximation or a decade from the text (with its
  next version).
- The ontology comments of `jl:birthDateNormalized` and `jl:deathDateNormalized` name the EDTF datatype (pull request
  to judaicalink-ontology).
- Consumers that need a year read the first year of an EDTF value (the Atlas does).
- First use: footprints 2026-10 (0034).
