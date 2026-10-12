# 0020 The kg-complements datasets in the framework: groupings, ontology terms, order

Status: accepted · Date: 2026-10-12

## Context

The 15 datasets made by `../kg-complements/` (2026-10-05/06; in `lokal/dumps-additions`, none published) are to be
made with the generator framework ([0018](0018-generator-framework.md)) and become versions in the catalogue.
Their builders mostly query the local QLever endpoint; in the framework they read the declared versions with its
reader and in-memory index, so the queries are rewritten (same logic, compared with the current outputs, measured
2026-10-12). Fifteen small datasets would crowd the catalogue, and the new ontology terms they use
(`ontology-complements`) were defined outside the ontology.

## Decision

### Groupings

`kind`, `method` and the automated flag belong to a whole dataset (0018), so parts are combined only where they
have the same kind and the same automated status, and belong together in content:

| From | Becomes | Kind / method |
|---|---|---|
| cm-journals, cm-structure | **a new version of `compact-memory`** (two files: journals, page structure) | support / converted |
| cm-entities-presence, cm-entities-wikidata | **`cm-entities`** (two files) | complement / deterministic, lookup |
| dates-normalized, places-linked, occupation-concepts, occupation-fix | **`records-normalized`** (four files) | complement / rule-based, deterministic (automated) |
| cm-ocr-quality | `cm-ocr-quality` | complement / statistical (automated) |
| gnd-persons-entityfacts | `gnd-persons-entityfacts` | records / lookup |
| nli-records | `nli-records` (replaces `nli-persons`, [0010](0010-nli-exception.md)) | records / converted |
| ls-nli-legacy | `ls-nli-legacy` | linkset / deterministic |
| quality-annotations | `quality-annotations` | complement / rule-based (automated) |
| ep-2026-10-06 | the entity-page set, last (how entity-page sets fit the version model is open) | entity-pages / rule-based (automated) |
| ontology-complements | **no dataset**: its terms go into the ontology (below) | – |

- `compact-memory` gets a new version rather than a successor dataset: the corpus data (journals, issues, pages)
  belongs to it. A new version may clean up: it is compared with the version it follows, and what it no longer
  states is documented in its description (decided 2026-10-12, for `compact-memory` after the comparison with
  2021-01-18: 4,710 of its 624,682 triples are dropped, see the version). The image links
  (`jl:hasVisualRepresentation`), which the kg-complements builder derived instead of stating, are stated for every
  page. `compact-memory-supp` stays its support data.
- Not combined: `cm-ocr-quality` (automated; it would flag the exact corpus data), `nli-records` and
  `ls-nli-legacy` (records and linkset; the linkset concerns only holders of legacy URIs),
  `gnd-persons-entityfacts` (records), `quality-annotations` (notes, partly about datasets).
- Result: 7 new datasets and a new version of `compact-memory`, instead of 15 datasets.

### Ontology terms: pull requests to judaicalink-ontology

- The ontology keeps its process: maintained as Markdown in judaicalink-ontology (<https://github.com/judaicalink/judaicalink-ontology>),
  the Turtle extracted from it (`generate.py`, a GitHub Action). New terms and corrections are proposed as pull
  requests, split into meaningful parts, so that they can be accepted openly; a new version of the dataset
  `ontology` is then imported from the repository (`jl import-files`, origin the file at its commit), as a
  preview until it is made stable. Branches are prepared and shown first; pushing and opening a PR needs the OK
  each time.
- Of the 45 terms of `ontology-complements`: 6 are in the ontology already (`belongsToIssue`, `belongsToJournal`,
  `birthLocationURI`, `deathLocationURI`, `gitCommit`, `gitWeb`; corrections only where they improve something);
  9 were only for the kg-complements `-meta` files and are dropped (`catalogueGraphIRI`, `category`,
  `namespaceSlug`, `describes`, `generationMethod`, `complements`, `linksetTarget`, and `gitCommit`, `gitWeb`), the
  framework's `-meta` uses standard vocabularies; 32 new terms in three pull requests:
  1. **Compact Memory and corpus presence** (16; PR 18, opened 2026-10-12): `subtitle`, `placeOfPublication`,
     `publicationPeriod`, `indexedPages`, `pageSequence`, `ocrKnownWordShare`, `meanOcrKnownWordShare`, and, instead
     of the six `cm…` properties on the entity (decided 2026-10-12: no corpus in term names), the class
     `jl:CorpusPresence` (one node per resource and corpus) with `jl:entity` (pointing to any JudaicaLink resource the
     node is about, not specifically an entity page), `jl:corpus`, `jl:mentionCount`, `jl:pageCount`,
     `jl:firstMentionYear`, `jl:lastMentionYear`, `jl:journalCount`, `jl:mostFrequentJournal`. The corpus is a
     resource of `compact-memory`, `data/compact-memory/corpus`; the nodes are coined by `cm-entities` as
     `data/cm-entities/presence/<entity IRI after data/>`. Examples go into the Markdown as indented code blocks
     (fenced blocks are extracted into the Turtle);
  2. **Normalised person data** (5): `birthDateNormalized`, `deathDateNormalized`, `birthDateUncertain`,
     `deathDateUncertain`, `occupationURI`;
  3. **Entity pages** (14): `EntityPage`, `Work`, `Subject`, `curationStatus`, `CurationStatus`, `Curated`,
     `AutomaticOnly`, `supportedBy`, `mergeDate`, `splitInto`, `splitDate`, `retiredDate`,
     `highestEntityPageNumber`, `previousEntityPageSet`; after the entity-page question is settled.
- The old metadata terms of the ontology (`hasGraph`, `isLoaded`, `gitCommit`, …) could be marked deprecated in a
  later pull request.
- **`jl:occupationURI`**, not `jl:occupationConcept`: the occupation as an IRI, next to `jl:occupation` (text),
  as `jl:birthLocationURI` is next to `jl:birthLocation`. Whether the IRIs that some datasets put into
  `jl:occupation` (against its range) are restated as `jl:occupationURI` is checked when porting
  `records-normalized`.

### Order

Each dataset becomes one version when it is finished (runs only until then, 0018):

1. `compact-memory` (new version), with the Compact Memory pull request;
2. `cm-ocr-quality`, `cm-entities`;
3. (order changed 2026-10-12: `records-normalized` reads `nli-records` and `gnd-persons-entityfacts`, which must be
   versions first) 3a `gnd-persons-entityfacts`; 3b `nli-records`, `ls-nli-legacy`; 3c `records-normalized`, with
   the person-data pull request; it complements the stable versions of the record datasets (in 2026-10-06 the
   endpoint held footprints 2025-03-21 and haskala 2025-03-24 instead; the port is first checked against the old
   output with those versions, then the stable ones are declared, decided 2026-10-12);
4. `quality-annotations`;
5. the entity-page set, with the entity-page pull request.

## Consequences

- `ontology-complements` and the kg-complements `-meta` writer are not carried over; `../qlever/make_inputs.py`
  reads the catalogue and the store once these datasets are versions.
- Not published, so renamed freely: `jl:occupationConcept` (23,810 triples in `ep-2026-10-06`, used by
  `ep_generator.py`, `../ep-demonstrator`, `../dashboard`) becomes `jl:occupationURI` when those are rebuilt.
- Inputs outside the catalogue (the CM bundle, the MODS files, the OCR file list, the NLI export, the web caches)
  get their homes as the datasets are ported: a support dataset, a file of the version, or an input made outside
  with origin and description (0018).
