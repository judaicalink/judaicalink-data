# 0030 Dublin Core: DCMI Metadata Terms only

Status: accepted · Date: 2026-10-18

## Context

Our datasets used both Dublin Core namespaces: the fifteen elements (`dc:`, `http://purl.org/dc/elements/1.1/`) in
footprints, nli-records, nrwbibdjg, hirsch-family and stolpersteine, the DCMI Metadata Terms (`dcterms:`) elsewhere,
so that titles were in `dc:title` and `dcterms:title` and queries had to ask for both. No source gives us DC Elements
in RDF; every use was our own choice. DCMI says that "most users can safely treat the fifteen parallel properties
as equivalent" and "gently encourages use of the /terms/ namespace". Since its release of 2020-01-20, `dcterms:creator`,
`contributor`, `publisher` and others have no `rdfs:range` any more (only `dcam:rangeIncludes`), and their usage
notes allow a literal where no URI can be given; the remaining ranges are `rdfs:Literal` (`title`, `date`,
`identifier`, …).

## Decision

- Our datasets write only `dcterms:`, also where a source uses the elements: `dc:<name>` becomes `dcterms:<name>`.
  A name as text stays a literal (e.g. `dcterms:creator "Lordick, Harald"` where the source does not identify the
  person).
- A run whose output has a property or class of DC Elements fails (`NOT_USED` in `src/jl/iris.py`, checked by
  `Run.write_turtle`); the error names the `dcterms:` term to use.
- The common layer of the ontology describes the `dcterms:` terms only.

## Consequences

- Published versions keep their `dc:` statements; readers of several versions (the entity pages) read both.
- The generators that still write `dc:` fail until they are changed, so their next version is corrected:
  nli-records (`dc:creator`), hirsch-family and stolpersteine (`dc:subject`, which also states the wrong thing:
  documents and images about the person, not its subject), footprints (with its new generator). nrwbibdjg is changed.
