# 0013 Catalogue entry format: datasets, versions, changelog

Status: accepted · Date: 2026-10-08 (proposed 2026-10-07; amended 2026-10-09: `aliases`, `inputs`, support data, no `authorlink`, changelog authors, dated legacy versions)

## Context

[0004](0004-complete-catalogue.md) keeps the Hugo format (Markdown with TOML front matter) and asks for
versions and a changelog. The current entries ([`catalog/README.md`](../../catalog/README.md)) describe one
state per dataset: a flat list of file URLs, a `graph` that is a namespace, a `dataslug` that is sometimes the
namespace and sometimes the dump directory, a `links` field holding link counts, and many empty fields.
Where the files are is decided separately ([0014](0014-locations-dataindex-finder.md)): entries name no
locations.

Compatibility with the current format is not a goal: judaicalink-site is adapted as soon as the new catalogue
is ready; Frankfurt gets the catalogue and its documentation and adapts their system.

## Decision

### Principles

- One file `<slug>.md` per dataset: TOML front matter between `+++` lines, Markdown body. The body is the
  full description of the dataset; it is the last resort for everything the fields do not cover (sources in
  detail, how the data was obtained, known problems). The part before `<!--more-->` is the summary.
- **Only `slug`, `title`, `author` and `license` are required.** Everything else is optional: an entry can
  describe a dataset without versions or files, a version without files, a file with only its path.
- A version lists exactly its own files. Descriptions are not repeated per version.
- Values that can be measured (size, checksum, triples) are written by the tooling where it can, never
  required.

### Dataset fields

| Field | Meaning |
|---|---|
| `slug` | **required.** The id of the dataset, used everywhere: file name `<slug>.md`, graph IRI and dataset IRI `http://data.judaicalink.org/datasets/<slug>` ([0006](0006-graphs-and-meta.md)), dump paths `<slug>/<version>/<path>` (0014), Hugo page URL `/datasets/<slug>/` |
| `title` | **required.** Name of the dataset |
| `author` | **required.** The current maintainer: name, or list of names |
| `license` | **required.** Table `name`, `uri`, `image` |
| `date` | date of the entry (Hugo; sorting) |
| `website` | the source of the data: the institution, project, website, API or dump location that owns or provides it (details in the body) |
| `links` | list of related links without predefined purpose: `[[links]]` with `url`, `label` (e.g. the online source, a generator, a paper, related support data) |
| `example` | an example entity URI |
| `picture` | logo of the source |
| `kind` | `records`, `complement`, `linkset`, `entity-pages`, `ontology`, `vocabulary`, `support` |
| `method` | how the data was made, list: `curated`, `scraped`, `converted`, `deterministic`, `rule-based`, `lookup`, `statistical`, `ai-generated` |
| `namespaces` | URI namespaces the dataset coins, list, relative to `http://data.judaicalink.org/data/` (sub-paths allowed: `nli/record`) |
| `replaces` | slugs of the datasets this one supersedes, list ([0007](0007-complementary-and-superseding-datasets.md)); the inverse (`replaced_by`) is derived by the tooling |
| `inputs` | slugs of our datasets this one is generated from, list (build order, rebuild triggers): datasets of any kind, support data included; no versions here: the versions and files a run used are recorded in the `-meta` file of the resulting version ([0006](0006-graphs-and-meta.md)), as are external sources |
| `generator` | table `repo`, `path`: the generator script |
| `stable` | version id of the recommended version (see below) |
| `withdrawn` | reason, if the dataset should no longer be used (e.g. a test index) |
| `aliases` | former URLs of the dataset's page on our sites, list of site-relative paths (Hugo redirects them to `/datasets/<slug>/`, so old links keep working) |
| `[files]` | descriptions of files, table path → text; only where a file needs one (the usual data file and `-meta` file are described by the dataset) |

### Versions

`[[versions]]`, one table per version, **in order, newest first**. The version id is any slug (lower-case
letters, digits, `-`, `.`), unique within the dataset, never changed or reused once published, as it is part
of every file path. The catalogue prescribes no scheme: generators coin version ids (default
`YYYY-MM-DD[-n]`, other schemes per dataset possible), hand-curated entries may use their own. A version
enters the catalogue only when it is added explicitly; experimental runs are not catalogued.

| Field | Meaning |
|---|---|
| `version` | **required (within a version).** Version id |
| `issued` | date the version was made |
| `author` | who made this version: name, or list of names (history; the dataset's `author` is the current maintainer) |
| `commit` | commit of the generator that made it |
| `graph` | only for legacy versions: the graph name used when it was loaded, if not the dataset IRI |
| `description` | short remark on this version |
| `withdrawn` | reason, if this version should not be used (known error) |
| `[[versions.files]]` | the files of this version: `path` (**required**, relative to `<slug>/<version>/`), optional `description` (overrides `[files]`), `bytes`, `sha256`, `triples` |

**Stable pointer.** `stable` names the recommended version. Versions listed above it are previews (newer, not
necessarily better), versions below it are older. Without `stable`, all versions are previews (a dataset in
testing). If a stable version turns out to be faulty, the pointer moves back and the version gets `withdrawn`.

**Counts.** Triples of a version = sum over its files; the dataset count is that of the stable (else the
newest) version. Computed by the tooling, not stated.

**New version or successor dataset.** Same slug = same graph, a new version takes the place of the old one in
the endpoints; a new slug = a separate graph that `replaces` the old one. Decided case by case (0007); a
substantially changed file structure usually means a new dataset.

### Changelog

`[[changelog]]`: `date`, `text`, optional `version`, `author` (name, or list of names) and `refs` (decision
numbers). Records what changed and why: new versions, stable pointer moved, superseded, files moved to the
archive, description changed. Only real changes to the dataset or its description are recorded, not changes
of the maintainer or of the entry format.

**Contributors.** Everyone who worked on a dataset is acknowledged: the contributors are derived from the
authors of the versions and of the changelog entries, not stored. Work that produced no version we still have
(an earlier state, a generator change that was never published) gets a changelog entry without `version`,
with its author; in doubt, a person is rather listed than left out. The catalogue pages show the changelog
and the contributors.

### Example

```toml
+++
slug = "nli-persons"
title = "Persons from NLI"
author = "Kai Eckert"
date = "2019-01-25"
website = "https://www.nli.org.il/"
example = "http://data.judaicalink.org/data/nli/Abner_"
kind = "records"
method = ["converted"]
namespaces = ["nli"]
stable = "2019-01-25"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"

[[versions]]
version = "2019-01-25"
issued = "2019-01-25"
author = "Maral Dadvar"
graph = "http://data.judaicalink.org/data/nli"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "nli-persons.ttl.gz"

  [[versions.files]]
  path = "nli-persons-meta.ttl.gz"

[[changelog]]
date = "2026-10-06"
author = "Kai Eckert"
text = "Superseded by nli-records; links from the legacy URIs in ls-nli-legacy."
refs = ["0007", "0010"]
+++

Persons extracted from the authority file of the National Library of Israel. …
```

```toml
+++
slug = "nli-records"
title = "NLI authority records"
author = "Kai Eckert"
website = "https://www.nli.org.il/"
kind = "records"
method = ["deterministic"]
namespaces = ["nli/record"]
replaces = ["nli-persons"]
generator = { repo = "https://github.com/judaicalink/judaicalink-data", path = "generators/nli_records.py" }

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"

[[links]]
url = "https://github.com/judaicalink/judaicalink-generators/tree/master/legacy/nli-persons"
label = "Legacy generator and input of nli-persons"

[[versions]]
version = "2026-10-06"
issued = "2026-10-06"
commit = "0000000"

  [[versions.files]]
  path = "nli-records.ttl.gz"
  triples = 0

  [[versions.files]]
  path = "nli-records-meta.ttl.gz"
+++

The person and work records of the NLI authority export behind nli-persons, one resource per record. …
```

(No `stable` yet: the one version is a preview.)

### Consumers

- **Catalogues and the finder**: [0014](0014-locations-dataindex-finder.md).
- **Generators**: the `-meta` file of a version is generated from the entry and the measured numbers; it names
  its version and contains no locations. `qlever/make_inputs.py` reads the catalogue (which version, which
  graph; replaced datasets are left out) instead of the `-meta` files.
- **Check**: `catalog.py check` parses every entry, checks the required fields, that `slug` equals the file
  name, that slugs in `replaces`/`inputs` and `stable` exist, that version ids are unique slugs, warns about
  `[files]` descriptions no version uses, and compares sizes and checksums with local files where present.

### Migration

Script-based, one commit, then curated by hand:

- the 36 entries get `slug` (file name) and one version with `graph` from the old entry, files from the old
  `files` (paths relative to the new `<slug>/<version>/`) and `stable` pointing to it (first run: `2026-09-26`
  for all, the date of the archived state; then curated, see below);
- `dataslug`/`namespace_slugs` → `namespaces`; `script` → `links`; `supportdata` (a catalogue URL, which entries
  must not name, 0014) → `inputs` of the main dataset, as it is generated from its support data;
  `referencedataset` dropped (the inverse, derived by the tooling); the old
  `links` texts (link counts) → body; `category = "support"` → `kind = "support"`; `files` descriptions →
  `[files]` only where they say more than the dataset (not when they repeat the title, the body or each
  other); non-empty `concepts`/`persons` counts go to the body like the `links` texts;
- `aliases` stay as they are; an entry without files (`occupations`) gets no version;
- bookmarklets are dropped (djh's maps an outdated site layout; rujen's is a copy of djh's);
- dropped: `productionurl`, `loaded`, `graph` at top level, `generator.gitweb` (→ `generator`/`commit`),
  `creators` (→ version `author`), `authorlink` (names only, no links to persons), empty fields (`concepts = ""`, `bookmarklet = ""`, …);
- `kind`, `method` by hand; `author` (current maintainer, the contact) is Kai Eckert for all; `cmtest` gets
  `withdrawn`;
- curation of the versions (2026-10-09): the archived state is the starting point, older states are not
  reconstructed. The version id and `issued` are the date of the newest file of the version: the time in the
  gzip header (the file's modification time when it was compressed), for tar archives named `.gz` the time of
  the member, else a date in the data, else the commit of judaicalink-site that first listed the file (file
  times in the archive are copy dates). The version `author` is who made the files;
- the history is reconstructed from judaicalink-site, judaicalink-generators, judaicalink-labs and
  judaicalink-ontology as changelog entries (earlier states, generator changes, description changes of
  persons not otherwise credited); the migration itself is not a change of the dataset and gets no entry;
- the archive is restructured to `<slug>/<version>/<path>`; the `-meta` files of `lokal/dumps-additions/`
  are added to these versions and regenerated without download URLs (0014);
- then entries for our new datasets.

## Open questions

- Redirects on archive.judaicalink.org from the old paths to the new ones, so that links in old publications
  and in Frankfurt's current catalogue keep working?
- Persistent identifiers (DOI, e.g. via Zenodo) for archived versions?
