# 0018 Generator framework

Status: **draft** (under discussion since 2026-10-10; points are added as they are agreed) · Date: 2026-10-10

## Context

From now on, every version we publish is made with one framework in `judaicalink-data`: the kg-complements
datasets first, then the migrated legacy generators. What does not depend on the data (versions, layout,
checksums, commit, inputs, `-meta`, comparison with a kept version, catalogue entry on request) is done by the
framework; a generator holds only the data logic (usually Python; another executable is possible). There is
no Django; there is a CLI for working with the datasets, maintenance and automation.

The past runs show what to keep and what to avoid ([generator history](../../generators/README.md)): the labs
`DatasetCommand` (one base, commit and script recorded, crawl kept as an input file: the reason rujen, yivo and
stolpersteine can be reproduced) and its faults (metadata in the code, drifting from the catalogue and naming
URLs; `git rev-parse HEAD` of whatever directory, no check for uncommitted changes; inputs and hand steps not
recorded; a token in public code). kg-complements repeated the metadata-in-code pattern, and its files are not
byte-reproducible (gzip header time, run time in the `-meta`).

## Decision (agreed so far)

### Three ways in, one way out

- **generate**: the framework runs the generator and writes the data files, the run record and the `-meta`.
- **import**: files made elsewhere (legacy code, a file someone sends) are taken in; the run record is written
  with what is known (may stay sparse).
- **re-meta**: the `-meta` of any or all versions is rendered again (e.g. after a change of the metadata model).
- The `-meta` is always rendered from the catalogue entry, the run record and measured statistics; generators
  never write metadata themselves.

### Run records

- One JSON file per version, `generators/<slug>/runs/<version>.json`, committed in `judaicalink-data` (public);
  not copied to the dumps.
- It holds the facts of how the version was made, enough to understand and redo it: date, commit, parameters,
  inputs, external sources with the time they were queried, hand steps, measured counts.
- Inputs are named as `<slug>/<version>/<path>` with checksum, or as an external URL with the query time; no
  local paths, no credentials (secrets come from the environment and are never recorded).

### The `-meta` file can be replaced

- The `-meta` file stays a file of its version, with size and checksum in the catalogue. When the metadata is
  rendered again, the file is replaced and the checksum in the entry updated; the change of the checksum in the
  git history documents the regeneration. Old `-meta` files are not kept; a checksum tells whether a copy was
  once an official file. This is the one exception to "archived files are never changed" ([0015](0015-dumps-clean-start.md)).
- It is only rewritten when its content has changed, ignoring the provenance of the metadata itself; so a
  changed checksum always means a real change.
- The provenance of the metadata (framework commit, time of creation, what it was made from) is part of the `-meta`.
- The self-descriptions written by the labs generators of 2020 (`yivo-metadata.ttl.gz`, `rujen-metadata.ttl.gz`,
  `rujen-translation-metadata.ttl`, `stolpersteine-metadata.ttl.gz`) were the former `-meta` of their versions. They
  held nothing beyond the catalogue except the generation time and the commit, which are documented in the generator
  READMEs (and go into the run records); they were removed from their versions on 2026-10-11 (changelog entries),
  amending [0015](0015-dumps-clean-start.md), which kept them. The regenerated `-meta` takes their place.

### URIs

All `http://data.judaicalink.org/…` (the form used throughout the data, checked 2026-10-10):

| What | URI |
|---|---|
| dataset (= graph) | `datasets/<slug>` |
| version | `datasets/<slug>/<version>` |
| file | `dumps/<slug>/<version>/<path>` |
| `-meta` graph | `datasets/<slug>-meta` |
| person | `datasets/agents/persons/<n>` |
| software agent | `datasets/agents/software/<name>` |

- URIs identify; they need not resolve. Locations stay out of the descriptions ([0014](0014-locations-dataindex-finder.md)):
  the file URI is the identifier of the distribution, `dcat:accessURL` is the finder, no `dcat:downloadURL`.
  If data.judaicalink.org later redirects `datasets/` and `dumps/`, the URIs resolve without rewriting.
- `datasets/` needs one server rule for everything below it (descriptions and agents); this is why agents are
  there and not in a top-level namespace.

### Agents

- Persons get sequential numbers, never reused, from a registry `catalog/agents.toml` (number → name, optional
  links, `withdrawn`); software agents keep descriptive names (e.g. `judaicalink-data` for the framework; its
  version goes into the activity as a commit).
- Names are only in the dataset `judaicalink-agents`, generated from the registry; the `-meta` files refer to the
  agent IRIs only. Who wants to credit a person by name can look it up there.
- The catalogue keeps names (`author`, version `author`, changelog): its pages can change at any time, while the
  `-meta` sets should not be regenerated only to remove a name. `catalog.py check` checks that every name is in the
  registry. If a person objects to being named, the name is removed from the registry, the agents dataset and the
  catalogue; the IRIs stay. (The git history keeps it.)

### Slugs and namespaces

- Reserved slugs: `agents`, and no slug may end in `-meta` (checked).
- `namespaces` in the catalogue lists only namespaces under `data/` (the knowledge graph). Everything under
  `datasets/` follows the fixed rules above and is not listed; the namespace check against the data looks only at
  `data/` URIs.

### Inputs and the index service

- Inputs are always declared as specific files or complete dataset versions. A declaration such as "all record
  datasets, stable versions" is resolved into explicit versions and files before the run and recorded so.
- Nothing besides the declared inputs is used. A SPARQL endpoint that is already running is never an input: it
  would have to be checked, and it leads to side effects (a rebuild of `places-linked` once counted its own
  earlier output, [0011](0011-reproducible-generation.md)).
- Where a generator wants SPARQL, the framework indexes exactly the declared input files and makes them available
  for the run (index service). The index is a means to an end: it speeds up or simplifies a generation. A full
  index of the graph (19.6 M triples, 123 files) took 24 s with QLever 0.6.0, so per-run indexes are affordable;
  an index can be reused while the input checksums are identical; each run uses its own port.
- The index service has a narrow interface (index these files, query, stop). One implementation uses QLever;
  which QLever (command or image) is local configuration. The run record names the service, its version and the
  index settings. Generators sort their results themselves (0011).
- Inputs that are not RDF (crawls, exports, caches) are read as files and declared with checksum like any input.

### Dump format: Turtle

- Data files are gzipped Turtle: smaller and more readable than N-Triples (measured 2026-10-11 on our datasets:
  uncompressed 34–72 % of the N-Triples size, gzipped 63–95 %).
- The framework writes Turtle deterministically: one fixed prefix set declared only at the top; subjects sorted,
  predicates sorted with `a` first, objects sorted; an empty line between subjects; gzip with a fixed header.
  Same triples, same bytes.
- For comparisons and line-based work the framework produces a canonical form: sorted, deduplicated N-Triples with
  normalised literals, made via the index service (so any Turtle can be read without a parser of our own). On it:
  a comparison API (identical, only added, removed) and a command to print the canonical form (grep, counting).

### No blank nodes

- No blank nodes. Imported files with blank nodes are reported (shape, count) before they are taken in.
- Rationale (for when the question comes up again): blank nodes get arbitrary labels from every parser, so the
  canonical form of two identical graphs can differ. Tree-shaped blank nodes (each referenced at most once, no
  cycles, written `[ … ]`) could still be compared by labelling them with a hash of their content; shared or
  circular ones need full canonicalisation (RDFC-1.0). A deterministic label in the file only fixes its bytes,
  not the comparison, because parsers relabel. Above all, complementary datasets ([0007](0007-complementary-and-superseding-datasets.md))
  can only add statements about IRIs, never about a blank node in another file. State of 2026-10-11: no blank nodes
  in any file of the catalogue versions (the only ones were in the four labs self-descriptions, removed, see above).

## Proposed, not yet discussed

- The `-meta` of a version describes the version and its dataset, including `replaces`, but not catalogue state
  that moves (`stable`, `replaced_by`); it states two dates: the version (fixed) and the metadata (changes).
- A version is only made from a clean working tree (or is marked).

## Consequences (so far)

- [0016](0016-data-access-outside.md) is amended: an index may be built temporarily for a generation run (part of the
  framework); SPARQL endpoints for data access stay outside.

## Open questions

5. Whether "standard library only" holds for migrated legacy generators (rdflib, scrapy).
6. One generator run for several datasets (nli-records + ls-nli-legacy, rujen + rujen-translation).
7. Build area and how a run becomes a version (`add-version` on request, `collect`).
8. The CLI: `catalog.py` extended, or a separate tool.
