# 0014 Locations, data index and dataset finder; how entries reach the catalogues

Status: accepted · Date: 2026-10-08

## Context

`judaicalink-data` is the definitive source of the dataset descriptions ([0003](0003-judaicalink-data-repository.md),
[0004](0004-complete-catalogue.md)). The descriptions are shown in several catalogues (web.judaicalink.org,
mannheim.judaicalink.org, the FID portal in Frankfurt), and the files of a dataset version can be in several
dumps locations (archive.judaicalink.org, mannheim.judaicalink.org, Frankfurt). The archive will not hold
every version. Locations change (the dumps moved from data.judaicalink.org to archive.judaicalink.org in
September 2026), and new ones may appear. If the `-meta` files or the catalogue entries named locations,
every such change would rewrite them and raise the question whether this makes a new version.

## Decision

### No locations in descriptions

Catalogue entries and `-meta` files never name a dumps or catalogue location. A file is identified by its
relative path `<slug>/<version>/<path>`, its size and its SHA-256 checksum; a copy from any location can be
verified with the checksum.

### Every location has the same structure

`catalog/locations.toml` names the known locations once, as prefixes:

```toml
[dumps]
archive  = "https://archive.judaicalink.org/dumps/"     # + <slug>/<version>/<path>
mannheim = "https://mannheim.judaicalink.org/dumps/"

[catalogues]
frankfurt = "https://www.jewishstudies.de/en/judaicalink/datasets/dataset/"   # + <slug>/
web       = "https://web.judaicalink.org/datasets/"
mannheim  = "https://mannheim.judaicalink.org/datasets/"
```

- A file is at `<dumps prefix><slug>/<version>/<path>`. `<path>` is relative to the version directory
  (usually the file name; subdirectories are allowed). The archive is restructured to this pattern
  (the old directories such as `epi/`, `dbpedia-person/`, `current/` go away; the catalogue links are what
  counts). Frankfurt adopts the structure when they next take over files.
- A dataset's catalogue page is at `<catalogue prefix><slug>/`. All catalogues return HTTP 404 for a slug
  they do not list (checked 2026-10-08 for Frankfurt and web.judaicalink.org).
- Moving a location to another server is one change in `locations.toml`.

### The data index (`dataindex.json`)

`catalog.py index` reads the entries and `locations.toml`, checks every file at every dumps location and
every dataset at every catalogue (HTTP HEAD), and writes `dataindex.json`: the time of the check, the
locations, and per dataset its title, `stable`, `replaces` and the derived `replaced_by`, the catalogues that list it, and its
versions (newest first) with their files (path, size, checksum, the dumps locations where the file was
found). Where the probe finds the file size, it is compared with the entry.

Only what can be found somewhere is in the index: a dataset only if a catalogue lists it or a file of it
was found; a version only if a file of it was found. Datasets in development do not appear.

The index is committed in `judaicalink-data` (a record of what was where, and when) and copied to the sites.

### The dataset finder

One static page with JavaScript, `https://web.judaicalink.org/dataindex/`, reads `dataindex.json`. It does no live checks: it
shows the state of the last index run, with its date. It takes the dataset, and optionally a version and
file, from the URL:

- `?dataset=<slug>` – dataset view (the stable version, else the newest, is the specified version);
- `?file=<slug>/<version>/<path>` – file view (dataset and version from the path).

The page shows:

1. **Not found**: if the dataset is not in the index, it says that no catalogue currently lists the
   dataset and no version of it is known, and asks to contact us if this seems to be a mistake (link to
   `/about-us/`).
2. Otherwise, **catalogues**: the catalogue pages that list the dataset, or a note that no catalogue
   currently lists it.
3. **The specified version** with all dumps locations of its files (every location where a file was found,
   so that another location can be tried if one fails or something was moved), or a note that no download
   location for this version is currently known. In the file view the requested file is shown first and
   prominently.
4. **Other versions** ([0013](0013-catalogue-format.md): `stable` pointer): if the specified version is not
   the stable one, a pointer to the stable version; newer versions than the stable one are mentioned as
   previews; if the specified version is the newest, a note that this is the most recent known version.
   A successor dataset (`replaced_by`) is pointed to as well.
5. **All versions**, shown only on request, with the specified version highlighted.

Each catalogue page of a dataset (on our sites; offered to Frankfurt) links to the dataset view of the
finder, so every catalogue leads to the state of the dataset across all locations.

### URLs in the `-meta` files

- `dcat:landingPage` of every dataset: `https://judaicalink.org/` (the landing page of the whole graph,
  not repeated per dataset).
- `dcat:accessURL` of every file: the finder in file view,
  `https://web.judaicalink.org/dataindex/?file=<slug>/<version>/<path>`. No `dcat:downloadURL`.
- The finder URL must not change once `-meta` files with it are published.
- **To discuss with Frankfurt:** the stable URLs should rather be on data.judaicalink.org (the host for
  stable JudaicaLink URIs) than on web.judaicalink.org. Until that is agreed we use web.judaicalink.org.

### How entries reach the catalogues

- **Curation by copying.** A dataset is shown in a catalogue of ours (web.judaicalink.org,
  mannheim.judaicalink.org) when its entry file is copied into that site (`content/datasets/<slug>.md`).
  Not copying it excludes it. There is no separate selection list.
- **`catalog.py sync --to <site>`** updates the entry files that are already in the site and copies
  `dataindex.json` (into Hugo's `data/`); it never adds or removes entries. Each copied file carries a
  comment, visible only in the Markdown source, that it is a copy from `judaicalink-data` and that changes
  go there.
- **Hugo shows only selected locations.** The site configuration names the dumps locations it exposes
  (`params.dumpLocations`, e.g. `["archive"]` for web.judaicalink.org, `["mannheim"]` for
  mannheim.judaicalink.org). The dataset template takes the files from `site.Data.dataindex` and shows only
  versions with a file at an exposed location, with links to these locations only. The stable version is
  shown as the current one, newer versions as previews.
- **Frankfurt** is not in our hands: they get the catalogue and its documentation and adapt their system
  to it; what they take over, they take over by hand ([0001](0001-roles-and-hosts.md)). The index shows what
  their catalogue lists (and, once they use the same dump structure, which files they offer).

## Consequences

- Changing, adding or losing a location changes only `locations.toml` and the next `dataindex.json`; no
  entry and no `-meta` file is rewritten, and no new version arises.
- The finder can point to versions that a site does not expose (e.g. newer versions on mannheim from
  web.judaicalink.org); the site's catalogue pages themselves show only their own locations.
- The index is a snapshot: after a move, the finder is right again after the next index run. `sync` runs
  the index first.
- A real redirect (`downloadURL`) could later be generated from `dataindex.json` as a server redirect
  table; not planned now, as it needs a change of the server setup.
- Built 2026-10-13: `jl update-dataindex` and `jl sync-site` (`src/jl/dataindex.py`; `sync-site --add` copies a new
  entry deliberately), `catalog/locations.toml` with the two catalogues `web` and `portal` (the FID portal; its
  catalogue URL forwards to `/de/` or `/en/` by language, the index follows redirects) and the two dumps locations
  `archive` and `data` (Frankfurt); the finder page and the templates in `judaicalink-site` (branch
  `catalogue-0014`, not published). The `-meta` files carry the landing page and the finder URLs. Until the
  archive holds the store, the index finds no files; `--assume archive=store --out FILE` makes a test index.
