# Catalogue

The complete catalogue of our version of the JudaicaLink data ([0004](../docs/decisions/0004-complete-catalogue.md)):
one file per dataset, `<slug>.md`.

## Origin of the current entries

The 36 entries were copied unchanged from `judaicalink-site/content/datasets/` (last change there:
`a49ca66`, 2026-09-26; the site's `_index.md` was not copied). Compared with the catalogue state
`81b42a5`, which is identical to what Frankfurt loaded (`portal/site/portal/judaicalink/backend/datasets/`;
only line endings differ in `date-enriched.md` and `geo-enriched.md`), they differ only in:

- dump URLs point to `https://archive.judaicalink.org/dumps/…` instead of `http://data.judaicalink.org/dumps/…`
  (same paths; archive = `lokal/dumps/`, see `lokal/dumps/README.md`);
- every entry has `productionurl`, the dataset page in the FID portal.

From now on this directory is the source of the catalogue. `judaicalink-site` keeps its copy as the archived
Mannheim catalogue; whether and how the site presents this catalogue later is still open.

## Format

The entry format is defined in [0013](../docs/decisions/0013-catalogue-format.md) (fields, versions,
changelog); locations are not part of the entries ([0014](../docs/decisions/0014-locations-dataindex-finder.md)).
`python3 catalog.py check` (repository root) checks all entries.

## Migration (2026-10-09)

The entries were converted to the format of 0013 by [`migrate_0013.py`](migrate_0013.py), as described in
0013 (section Migration), from the old entries in the commit before it; sizes and checksums were measured on
the local copy of the archive. The script is kept as the record of the conversion; it only reads the old
format and cannot be run again on the migrated entries. Hand curation follows in separate commits; the
first one gave every version the date of its newest file as id and reconstructed the changelogs (0013,
section Migration).

## Former format (until 2026-10-09)

This is the format of the archived catalogue in `judaicalink-site` and of the Frankfurt catalogue.

Markdown with a TOML front matter between two `+++` lines, as used by Hugo
(<https://gohugo.io/content-management/front-matter/>). The body is the description in Markdown; the part
before `<!--more-->` is the summary shown in lists.

```toml
+++
title = "Entity Pages - Judaicalink"
author = "Marco Rovera"
authorlink = "http://…"
date = "2021-01-22T10:37:07+02:00"
category = "judaicalink"
dataslug = "ep"
graph = "http://data.judaicalink.org/data/ep"
example = "http://data.judaicalink.org/data/ep/1000037"
loaded = true
productionurl = "https://www.jewishstudies.de/en/judaicalink/datasets/dataset/ep/"

[[files]]
	url = "https://archive.judaicalink.org/dumps/ep/entity_pages.ttl.gz"
	description = "Entity Pages RDF data (2098149 triples)."

[license]
name = "CC0"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
+++

Description in Markdown.

<!--more-->
```

### Fields in use

Count = number of the 36 entries that have the field (many entries carry empty strings for unused fields).
Readers: **H** = Hugo template `judaicalink-site/layouts/datasets/single.html`;
**F** = Frankfurt portal (`judaicalink/datasets/views.py` and `templates/datasets/detail.html`).

| Field | Count | Read by | Meaning |
|---|---|---|---|
| `title` | 36 | H F | name of the dataset |
| `date` | 36 | F | date of the entry (F sorts the list by it); not consistently creation or update date |
| `author`, `authorlink` | 36 | H F | maintainer, shown as "Maintained by" |
| `category` | 36 | F | `judaicalink` (29) or `support` (7: data that supports a dataset, e.g. caches, label lists) |
| `license` (`name`, `uri`, `image`) | 36 | H F | licence |
| `productionurl` | 36 | H | dataset page in the FID portal (added for the archived Mannheim catalogue) |
| `files` (`url`, `description`) | 35 | H F | dumps; H and F show RDF icons by file extension. 13 entries also have `filename`, `filepath` |
| `loaded` | 32 | H | whether loaded in "our" SPARQL endpoint (F checks this live instead) |
| `graph` | 31 | F | named graph in the triple store; mostly the namespace `…/data/<x>`, for yivo/rujen `…/datasets/<x>` |
| `dataslug` | 27 | H F | URI namespace `…/data/<dataslug>/`; F also uses it as dump directory and Solr filter (fallback: file name) |
| `example` | 25 | H F | example entity URI |
| `website` | 17 | H F | website of the source |
| `links` | 11 | H | free text on links to other datasets |
| `aliases` | 8 | (Hugo) | old URLs of the page |
| `script` | 7 | H | link to the generator script |
| `picture` | 7 | H | logo of the source |
| `referencedataset`, `supportdata` | 4, 4 | H | link between a dataset and its support data |
| `concepts`, `persons` | 4 | H | free-text counts |
| `bookmarklet` | 4 | H | bookmarklet for the source website |
| `creators` (`name`, `url`) | 4 | – | creators (written by the labs generators) |
| `generator` (`script`, `gitweb`, `commit`) | 4 | – | generator with commit (written by the labs generators) |
| `slug`, `namespace_slugs` | 3 | – | written by the labs generators (yivo, rujen, rujen-translation) |
| `description`, `keywords` | 1 | (Hugo) | only `_index.md` of the site |

F also reads `solr_core` (not used in any entry). Hugo and Frankfurt parse the front matter with
different TOML parsers (Go; Python `toml` package): entries must stay valid for both.

### Known problems of the former entries

- `dataslug`, `graph`, dump directory and URI namespace do not match in several entries: epidat
  (`dataslug`/`graph` `epi`, URIs `data/epidat/`), dump directories `dbpedia-person`, `stolpersteine`,
  `ubffm`, `nli`, `judaicalink-ontology` for the entries `dbpedia-persons`, `stolperstein` (renamed `stolpersteine`, 0017), `ubffm-persons`,
  `nli-persons`, `ontology`; no `dataslug` for yivo, rujen, rujen-translation, date-enriched,
  dbp-wiki-geo-linking; `graph` of geo-coordinates is `data/geo-coor`.
- `graph` names a namespace, not the graph of the dataset ([0006](../docs/decisions/0006-graphs-and-meta.md)).
- Dump paths ending in `/current/` were changeable directories, not versions.
- `occupations` (added by Frankfurt in December 2025) has no dump anywhere.
- `cmtest` is a test index (Elasticsearch JSON), not a dataset.

The entries are to be migrated to the new entry format accepted in
[0013](../docs/decisions/0013-catalogue-format.md); locations, the data index and how entries reach the
catalogues are decided in [0014](../docs/decisions/0014-locations-dataindex-finder.md).
