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
- Built 2026-10-11: `catalog/agents.toml` with the eight persons named in the catalogue, numbered in the order of
  their first contribution recorded there, and the software agent `judaicalink-data`; `jl check-catalog` checks
  the registry and that every name is in it, `jl list-agents` shows it. The dataset `judaicalink-agents`
  (`kind = "support"`, no version yet) is generated from it (`generators/judaicalink-agents`): persons with
  `foaf:name` and optional `rdfs:seeAlso` links, a withdrawn person with the IRI only; software agents with
  label and homepage.

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

- Built 2026-10-11 (`jl add-version`, `src/jl/versions.py`): it also refuses failed runs, runs with a run as
  input, a version id that is reserved or taken, and an author not in the agents registry (default author:
  `git config user.name`); `issued` is the run date. Header comments go only into the Turtle files the generator
  wrote (copied inputs keep their bytes and checksum). `--store-only <path>` keeps a file of the run in the
  store without listing it in the catalogue (the version's run record names it, and `check-catalog --complete`
  accepts it). It warns when an input made outside has no URL as origin. The version's run record is the run
  record plus `version` and the files as they are in the version (size and checksum after the header); the run
  directory keeps its record and log. The catalogue entry is edited as text (comments and layout stay); each
  edit is checked by parsing the result and comparing it with the expected data, otherwise nothing is written.
  `--dry-run` writes the version into the build area (`<run-id>-as-<version>/`, with the entry as it would be)
  and changes nothing else.
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

### Inputs and the index

- Inputs are always declared as specific files or complete dataset versions. A declaration such as "all record
  datasets, stable versions" is resolved into explicit versions and files before the run and recorded so.
- Nothing besides the declared inputs is used. A SPARQL endpoint that is already running is never an input: it
  would have to be checked, and it leads to side effects (a rebuild of `places-linked` once counted its own
  earlier output, [0011](0011-reproducible-generation.md)).
- **Generators read their RDF inputs with the framework's own reader and index** (decided 2026-10-11), not
  with a triple store: an implementation of our own, standard library only, that stays stable for years and
  gives the triples exactly as they are in the files. The index holds the declared input files in memory and
  answers triple patterns (objects of a subject and predicate, subjects of a predicate and object, any pattern
  with wildcards); joins are written in Python. Results come in file order, so they are deterministic for the
  same inputs; generators still sort what they write (0011). Our inputs are small enough for this (13.5 M
  distinct triples in all versions together, far fewer per generator; measured: cm-tagme, 6.0 M triples, loads in
  33 s and takes 2.7 GB).
- No SPARQL during generation. The first plan was an index service that builds a QLever index per run (a full
  index of the graph took 24 s with QLever 0.6.0). It was built and tested (commit `80d09ec`) and then dropped:
  QLever normalises literal values (see Dump format), so a generator would have had to take every literal from
  the files and only select and join with SPARQL, a rule that is easy to break without noticing; it would also
  have tied generation to an external program and its version. None of our generators uses SPARQL (the
  kg-complements generators read the dump files). If a generator ever needs SPARQL, that is a new decision.
  SPARQL endpoints stay outside the framework ([0016](0016-data-access-outside.md)); which engine serves
  mannheim.judaicalink.org is compared separately (`../endpoints/`).
- Inputs that are not RDF (crawls, exports, caches) are read as files and declared with checksum like any input.

### Dump format: Turtle

- Data files are gzipped Turtle: smaller and more readable than N-Triples (measured 2026-10-11 on our datasets:
  uncompressed 34–72 % of the N-Triples size, gzipped 63–95 %).
- The framework writes Turtle deterministically: one fixed prefix table (a file declares the prefixes it uses,
  sorted, only at the top); subjects sorted, predicates sorted with `a` first, objects sorted (in the order of
  their canonical N-Triples form); an empty line between subjects; literals always quoted with their datatype as
  given (no number shortcuts, so the lexical form is visible); gzip with a fixed header. Same triples, same bytes.
- For comparisons and line-based work the framework produces a canonical form: sorted (by code point, the order
  of `LC_ALL=C sort`), deduplicated N-Triples, normalised only where RDF 1.1 term equality allows (no
  `xsd:string`, lower-case language tags). On it: a comparison API (identical, only in a, only in b) and commands
  to compare and to print the canonical form (grep, counting). Canonical forms are cached by file checksum.
- **The framework reads RDF itself** (N-Triples and Turtle, standard library), not via QLever as first
  planned: QLever normalises literal values when it indexes (measured 2026-10-11 with QLever 0.6.0:
  `xsd:integer` becomes `xsd:int`, `xsd:float` becomes a rounded `xsd:decimal`, dateTime is cut to milliseconds,
  WKT points are reformatted, an ill-typed literal aborts the whole index). That affects real data
  (cm-tagme, date-enriched, gba, epidat, hhkeydocs, sosy). The reader handles every RDF file of the catalogue
  versions (74 files, 13.7 M statements, about 1 minute; tar archives named `.ttl.gz`; the one RDF-star
  statement in epidat is left out and counted); on all graphs it gives the same triples as QLever except
  exactly these normalisations.

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
  Turtle writer, reading by its reader (see Dump format).
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
  The framework is the package `src/jl/` (catalogue, configuration, runs, RDF reader, Turtle writer and
  canonical form, index, `-meta` rendering, store). Local settings in `local.toml` (not committed;
  template `local.example.toml`): store, build area, cache, legacy dumps.
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
  declarations are module constants, versioned with the code: `INPUTS` (name → reference) and `PARAMS` (name →
  default); and a function `generate(run)`. The run object gives the inputs (`run.input`, `run.inputs`, checked
  against their checksums), the reader and index (`run.triples`, `run.graph`), the parameters, a log and notes for
  the run record, and the writers (`run.write_turtle`, `run.copy_input`, `run.path` for other files); everything
  goes into the run directory. `jl generate <slug> [--param k=v] [--input name=ref]`; overrides are recorded.
- Input references: `<slug>/<version>/<path>` (one file of a version), `<slug>/<version>` (its RDF data files
  without the `-meta`), `<slug>/<run-id>[/<path>]` (development only; `add-version` refuses it), `repo:<path>` (a
  file of this repository, e.g. `catalog/agents.toml`: fixed by the commit like the code, so uncommitted changes
  to it count as uncommitted code), and for a file
  made outside that is in no version yet `{sha256, bytes, origin, description}`: found by checksum in the store
  and in the `sources` directories of `local.toml`. Both texts are required and go into the run record: `origin`
  says where we got the file (a URL where there is one, e.g. the file in a git repository at a commit; otherwise
  text, e.g. who sent it when), `description` what it is (content, format, who made it and how). `add-version`
  does not copy such a file anywhere: whether an input is kept with a version (published or in the store) is
  decided per file (0019). It warns when an origin is not a URL, so that this decision is made for a file that
  is found nowhere else (decided 2026-10-11: the more the origin is not durable, the more the description
  matters).
- The run record (`run.json`): slug, run id, generator path, commit of this repository and the files of the
  generator and the framework that had uncommitted changes, Python version, parameters, input overrides, the
  inputs (reference, file name, checksum, size), status (and the error of a failed run), start and end, notes,
  and the files written (path, size, checksum, triples). Failed runs keep their directory and record.
- **Imports** (built 2026-10-11, `jl import-files`): `import-files <slug> <files…> --origin … --description …`
  takes files made elsewhere in as a run (mode `import`, the framework's commit; files kept byte for byte, no
  header comments; RDF files with blank nodes refused), which `add-version` makes a version (`--issued` for the
  date the data was made). `import-files <slug>/<version> --description … [--origin …] [--source URL]… [--note …]`
  attaches a run record (mode `import`) to a catalogued version made outside the framework; no file of the
  version changes. The record holds what is known: description, origin, sources (code and documentation at
  their commits), notes, and the files with size, checksum and triples. In the `-meta`, the generation of such a
  version is described by these texts and links (`rdfs:comment`, `rdfs:seeAlso`), not by `prov:used`, as the
  evidence varies (exact, probable, unknown) and is given in the generator README.
- Run records under `generators/<slug>/runs/` are not code: they do not make a generator count as uncommitted.
- Done 2026-10-11 for all 33 legacy versions (commit `bc4a2ff`): each has an import record with the generator
  README and the original files of that version (`generators/originals.json`; for the datasets with two versions
  chosen by commit) as sources, the evidence and reproducibility of `generators/README.md` as a note, and for
  stolpersteine 2020-10-06, rujen 2020-09-28 and hirsch-family 2018-10-30 a note that the framework generator
  reproduces it. `render-meta --all` then gave every version its `-meta` (in the store and the catalogue, not yet at
  any dumps location; 7 s with the canonical cache); a second run left all 34 unchanged.
- Tested 2026-10-11 on three generators, each a faithful port of the original code with no change to its logic:
  stolpersteine (crawl of 2020-10-06), rujen (crawl of 2020-09-28) and hirsch-family (CSV of `40f7c98`, by
  checksum and origin) give exactly the triples of their kept versions (1,119, 140,472, 506).

### The `-meta` content (built 2026-10-11, to be reviewed)

Rendered by `jl add-version` and `jl render-meta` (`src/jl/meta.py`) from the catalogue entry, the run record of
the version and statistics measured on its files; gzipped Turtle with header comments, graph `datasets/<slug>/meta`.
It describes the version and its dataset, but no catalogue state that moves (`stable`, `replaced_by`, the
maintainer, the contributors), so moving `stable` rewrites no `-meta` (the proposal of 2026-10-11). Two dates:
the version's `dcterms:issued` (fixed) and the end of the metadata rendering (changes).

- **Dataset** `datasets/<slug>`: `dcat:Dataset`, `void:Dataset`; identifier, title, description (the summary of
  the entry), licence, `dcterms:source` (website), `void:exampleResource`, `void:uriSpace` per namespace,
  `dcterms:replaces`, `dcat:landingPage` (0014), `dcat:hasVersion`.
- **Version** `datasets/<slug>/<version>`: also `prov:Entity`; `dcat:isVersionOf`, `dcat:version`, issued,
  description, `dcterms:creator` (the version's authors, by IRI), `owl:deprecated` if withdrawn; measured on the
  union of its RDF data files: `void:triples`, `void:distinctSubjects`, `void:properties`, `void:classes`;
  `dcat:distribution` for each published file and the `-meta` itself; `prov:wasDerivedFrom` the input versions.
- **Files** `dumps/<slug>/<version>/<path>`: `dcat:Distribution` with description, `dcat:accessURL` (the finder,
  0014), media type and compression (IANA IRIs, where registered), `dcat:byteSize`, `void:triples`, and the
  checksum as `spdx:checksum` `<file IRI>#sha256` (an IRI, as there are no blank nodes). The `-meta` file has no
  size or checksum of its own. Files kept only in the store are not described.
- **Generation** `datasets/<slug>/<version>/generation` (versions with a run record): `prov:Activity` with start
  and end, associated with the software agent `judaicalink-data` and the version's authors; `prov:used` the
  generator at its commit (GitHub URL), the input files (file IRIs; `repo:` files at the commit; outside inputs by
  their origin URL), a comment for each outside input (file, size, checksum, description, origin), the
  parameters and notes as comments, `rdfs:seeAlso` the run record in the repository.
- **Provenance of the metadata** `datasets/<slug>/<version>/metadata`: `prov:Activity` with end time, the software
  agent, `prov:used` the framework at its commit; the `-meta` file `prov:wasGeneratedBy` it. `render-meta`
  compares the content without these triples (about or linking to this activity) and rewrites the file, and its
  size and checksum in the entry, only when the content changed. Both commands refuse uncommitted framework
  code (except `--dry-run`, `render-meta --out`).

Tested 2026-10-11: `add-version --dry-run` on the clean hirsch-family run (data file identical to the version
2018-10-30 except for the header; `-meta` 54 triples), `render-meta --out` on the legacy versions of rujen and
stolpersteine; unit tests on a temporary catalogue and store (add, refuse, render unchanged, render after a
change of the entry). No version was added to the real catalogue.

## Consequences (so far)

- [0006](0006-graphs-and-meta.md) is amended: all RDF files of a version form the dataset graph; the metadata graph
  is `datasets/<slug>/meta`.
- [0016](0016-data-access-outside.md) stays as it is: generation uses no SPARQL endpoint (the amendment drafted
  earlier, a temporary QLever index per run, was dropped on 2026-10-11); the framework's index is its own, in memory.

## Open questions

- None of the original list. The first generators (stolpersteine 2020, rujen, hirsch-family) confirmed the
  design (see The CLI and the generators); `add-version`, `render-meta` and `import-files` are built, and every
  version has a `-meta` (2026-10-11).
- To review in the `-meta` content: `kind` and `method` of the entry (`ai-generated` matters to users) have no
  property yet; the legacy `graph` of a version is not stated; the full description (body) is not included, only
  the summary; checksums as `<file>#sha256` IRIs.
