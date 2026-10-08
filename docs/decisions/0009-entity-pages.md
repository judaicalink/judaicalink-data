# 0009 Entity pages: one set at a time, core classes, precedence, IRI lifecycle

Status: accepted · Date: 2026-10-06

## Context

Entity pages are the hub of the knowledge graph: one page per entity, combining what all datasets say.
The legacy entity pages (2019, `ep` dumps) had 1.7 million pages, most of them for Compact Memory
mentions and pages. Errors are unavoidable; merges and splits must keep the URIs stable so that the data
can be improved step by step.

## Decision

- **One set at a time:** `ep-<date>` (`ep-<date>-<n>` for a further run on the same day), generated from
  the previous set and all records; it replaces the previous set (`dcterms:replaces`).
- **Core classes:** persons, places, works, subjects. Pages resting only on automatic data (e.g. TagMe in
  Compact Memory OCR) are kept and flagged `jl:curationStatus jl:AutomaticOnly`, not deprecated.
- **Precedence of datasets:** GND > libraries and bibliographies > curated reference works > general
  knowledge bases > automatically derived data; languages English > German > Hebrew > others. The preferred
  name is the GND form, else the most common form.
- **Clustering:** previous clusters stay together; new merges only through identity keys (GND, Wikidata,
  GeoNames, VIAF, LC, `owl:sameAs` between records), with guards against joining different Wikidata items
  (and, for VIAF/LC, different GND numbers).
- **Merge:** the page keeps the URI with the most records (or the oldest number); it still stands for what
  it stood for. Other URIs point to it: `dcterms:isReplacedBy` + `jl:mergeDate`.
- **Split:** a page that stood for several entities becomes a pointer (`jl:splitInto` + `jl:splitDate`);
  all parts get new URIs, or the URI of the page they already have.
- **Retired:** pages outside the core stay resolvable: `jl:retiredDate`.
- **One statement per event**, the date of the run; merged or split pages are no longer pages without saying
  so. History is never rewritten: event statements of earlier sets are copied unchanged; chains are followed
  when resolving.
- **URIs are never reused:** new pages get numbers above the highest number ever used
  (`jl:highestEntityPageNumber` in the set's `-meta`).

## Consequences

Details, counts and the list of obsolete dumps: `dumps-additions/ep-2026-10-06/README.md`; generator
`ep_generator.py`. Exception: [0010](0010-nli-exception.md).
