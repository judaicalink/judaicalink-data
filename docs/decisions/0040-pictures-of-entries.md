# 0040 Pictures of catalogue entries are files of the catalogue

Status: accepted · Date: 2026-10-31 · Amends [0013](0013-catalogue-format.md)

## Context

Four entries (djh, rujen, rujen-translation, yivo) named their logos by paths of web.judaicalink.org (`/img/…`). Every
other place that shows the catalogue (the FID portal, the Mannheim platform) showed a broken image, or had to depend on
that site.

## Decision

- **The pictures of an entry are files in `catalog/pictures/<slug>/`**, any number of them, e.g.
  `catalog/pictures/yivo/logo.jpg`. The field `picture` names the logo by its path relative to `catalog/`
  (`pictures/yivo/logo.jpg`). `jl check-catalog` checks that the file is in the entry's folder, exists, and is a PNG,
  JPEG, SVG or WebP image (a warning above 500 KB).
- **Every place that shows the catalogue copies the pictures with the entries** and serves them itself:
  `jl sync-site` copies them to `static/catalog/pictures/<slug>/` of the site (served at
  `/catalog/pictures/<slug>/…`); the portal keeps them beside its copy of the entries. No site depends on another.
- **Not in the `-meta`**: the pictures have no permanent public URL.
- Logos belong to their institutions; we keep them only to name the source on its entry.
