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
  once an official file. This is the one exception to "the files of a version are never changed" ([0019](0019-dumps-locations-equal.md)).
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
| metadata graph (the `-meta` file of the loaded version) | `datasets/<slug>/meta` |
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
  `-meta` sets should not be regenerated only to remove a name. `jl check-catalog` checks that every name is in the
  registry. If a person objects to being named, the name is removed from the registry, the agents dataset and the
  catalogue; the IRIs stay. (The git history keeps it.)

### Slugs and namespaces

- Reserved: the slug `agents`, and the version ids `meta` and `current` (checked).
- Everything about a dataset is below its IRI: versions `datasets/<slug>/<version>`, metadata graph
  `datasets/<slug>/meta`. This replaces the graph `datasets/<slug>-meta` of [0006](0006-graphs-and-meta.md)
  (used only in unpublished files and the local index).
- `namespaces` in the catalogue lists only namespaces under `data/` (the knowledge graph). Everything under
  `datasets/` follows the fixed rules above and is not listed; the namespace check against the data looks only at
  `data/` URIs.

### Runs, graphs and files

- **Default and recommended: one generator, well-defined inputs, one run, one version of one dataset.** The run
  record belongs to that version. Datasets that belong together share code, not runs (nli-records and
  ls-nli-legacy share the module and the NLI export as input); a dataset that needs another one's output declares
  that version as an input. Running several generators in a row (in `inputs` order) is a convenience of the CLI.
- Other ways are possible where there is a reason, documented in the run records: an input made outside or by a
  separate script and then turned into RDF by the generator; an intermediate RDF made in a first run and worked on
  in a second; files made entirely outside (import). Each step's output is an input of the next, named by checksum.
- **Graphs:** all RDF files of a version form the graph `datasets/<slug>`; its `-meta` file goes into
  `datasets/<slug>/meta`. One metadata graph per dataset (not per version): only one version of a dataset is
  loaded in an endpoint, and replacing the metadata is replacing one graph. Not a shared or default graph.
- **Files:** our generators write one data file `<slug>.ttl.gz` by default, plus `<slug>-meta.ttl.gz` and any
  published inputs; several RDF files only where splitting helps users (e.g. a large part that is often not
  needed). Legacy versions keep their files.

### From a run to a version

1. **Run:** `generate <slug>` writes into the build area, `<build>/<slug>/<run-id>/`: output files, run record, log.
   The run id is `run-` and a UTC timestamp (`run-20261011T143000Z`), so it is always recognisable as a run;
   no run overwrites another. Experimental runs may use uncommitted
   code; the run record notes the commit and whether there were uncommitted changes.
2. **Check:** compare with a kept version, load, count; all on the run directory.
3. **Version, only on request:** `add-version <slug>/<run-id>` refuses runs from uncommitted code; gives the version
   id (default the run date `YYYY-MM-DD`, `-n` if taken); writes the header comments and renders the `-meta` for
   that version; copies the run record to `generators/<slug>/runs/<version>.json`; adds the version to the catalogue
   entry (published files with size, checksum, triples; `issued`; author; commit) with a changelog entry; moves the
   files into the store `<slug>/<version>/<path>` ([0019](0019-dumps-locations-equal.md)). It does not move `stable`.
4. **Publish, on request:** copy the files chosen for publication from the store to a dumps location; the index
   records it.

- The triples of a data file contain no version id and no file URIs; only the `-meta` does. So any run can become
  any version, and experimental runs use up no version ids. (Dates such as the run date in entity-page events are
  data, not version ids.)
- The store is the local master tree of all versions (`lokal/store`, formerly `dumps-new`, [0015](0015-dumps-clean-start.md)).

### File names and `current`

- File names carry no version; the path does: `<slug>/<version>/<slug>.ttl.gz`. The names stay the same across
  versions, so `[files]` descriptions in the catalogue apply to every version, and legacy versions follow the same
  convention.
- Our Turtle files identify themselves by a header comment, written by `add-version`:
  `# JudaicaLink dataset <slug>, version <version>` and the version IRI. Comments are not triples, so the graph
  holds no version id; a downloaded file still says what it is. Files without comment syntax (JSONL) are
  identified by path and checksum.
- A dumps location may offer `<slug>/current` as a symlink to the stable version of the catalogue, maintained by
  the publish step; `current` is a reserved version id. It is a convenience only: never named in the catalogue,
  the `-meta` or the run records, which always name the real version. Side effect (checked 2026-10-11): 34 of the
  82 old paths on archive.judaicalink.org (`<slug>/current/<file>`) resolve again.

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

### Third-party packages: acquisition and transformation

- **Transformation** (declared inputs → the files of a version) uses only the standard library and the framework.
  It is what is re-run and compared, and it has to keep working for years (the legacy generators broke on
  Python 2's `urllib2`, rdflib and scrapy versions). rdflib is not needed: writing is done by the framework's
  Turtle writer, reading by the index service.
- **Acquisition** (crawling, web APIs, translation, NLP) may use third-party packages, pinned with exact versions in
  `generators/<slug>/requirements.txt`; the framework checks the installed versions and records them in the run
  record (setting up the environment is left to whoever runs it). Its output is always a file with a checksum,
  which becomes an input of the transformation. Re-running an acquisition gives a new input, so a new version.
- This is the lesson of rujen, yivo and stolpersteine: they can be reproduced because the crawl was kept.

- An acquisition output belongs to the version it was made for, or to a support dataset (`kind = "support"`, own
  versions, named in `inputs`) when several datasets use it (e.g. `compact-memory-supp`). The run record names it
  by checksum in every case.
- Whether it is published in the dumps or only kept in the store is decided per file and can be reversed
  ([0019](0019-dumps-locations-equal.md)): published where it is worth it (e.g. the crawls of rujen, yivo,
  stolpersteine, files of their versions), the store where it is large, private or of little use to others
  (e.g. the CM export bundle).
- The web caches of the lookup datasets (Wikidata, DNB EntityFacts) are kept in the store and referenced by
  checksum (2026-10-11: 372 MB, of which 97 Wikidata answers with complete entities make 365 MB).

### The CLI and the generators

- One tool, `jl` (`./jl <command>`, standard library, no installation); it replaced `catalog.py` on 2026-10-11.
  The framework is the package `src/jl/` (catalogue, configuration, runs, Turtle writer and canonical form,
  `-meta` rendering, index service, store). Local settings in `local.toml` (not committed; template
  `local.example.toml`): store, build area, legacy dumps, QLever command or image, port range.
- Commands are verb-noun, so that none is ambiguous:

| Group | Commands |
|---|---|
| Read access | `list-datasets`, `show-dataset <slug>`, `list-versions <slug>`, `show-version <slug>/<version>`, `list-runs <slug>`, `show-run <slug>/<run-id>`, `list-agents` |
| Generating | `generate <slug> [--param k=v]`, `import-files <slug> <files…>` (files made elsewhere become a run), `compare <a> <b>` (runs or versions), `show-canonical <file>` |
| Versions and metadata | `add-version <slug>/<run-id>`, `render-meta <slug>[/<version>]` or `--all` |
| Catalogue and store | `check-catalog`, `collect-store` (migration), `update-dataindex` ([0014](0014-locations-dataindex-finder.md)), `sync-site`, `publish-version <slug>/<version> --to <location>`, `status` |

- The read commands show what the framework parsed and derived: `show-dataset` the entry fields plus contributors,
  `replaced_by`, the stable version and its triple count; `show-version` the files with size, checksum, triple count
  (per file and for the version), public or store only, where found, and a summary of the run record; `show-run`
  the run record, output files, the end of the log and whether it became a version. `--json` gives the parsed
  structure (for checking and automation).
- Identifiers: `<slug>` (dataset), `<slug>/<version>`, `<slug>/<run-id>`; a version is a run that was made a version.
- A generator is `generators/<slug>/generate.py`: a Python entry point (it may call other programs) whose
  declarations (inputs as specific versions or files, default parameters) are module constants, versioned with the
  code; the run record holds the values actually used. To be tested on the first generators.

## Proposed, not yet discussed

- The `-meta` of a version describes the version and its dataset, including `replaces`, but not catalogue state
  that moves (`stable`, `replaced_by`); it states two dates: the version (fixed) and the metadata (changes).

## Consequences (so far)

- [0006](0006-graphs-and-meta.md) is amended: all RDF files of a version form the dataset graph; the metadata graph
  is `datasets/<slug>/meta`.
- [0016](0016-data-access-outside.md) is amended: an index may be built temporarily for a generation run (part of the
  framework); SPARQL endpoints for data access stay outside.

## Open questions

- None of the original list; the first generators (rujen from its crawl, stolpersteine 2020, hirsch-family) test
  the design.
