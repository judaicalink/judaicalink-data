+++
slug = "compact-memory"
title = "Linking Compact Memory - Pages"
author = "Kai Eckert"
date = "2021-01-19"
namespaces = ["compact-memory"]
inputs = ["compact-memory-supp"]
stable = "2021-01-18"
kind = "support"
method = ["converted"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/compact-memory"

[files]
"cm_tagme_pages.ttl.gz" = "Page metadata in RDF for Compact Memory, for pages where entity references have been found (624682 triples)."
"compact-memory-journals.ttl.gz" = "The journals: title, subtitle, place of publication, publisher, period, language, ZDB and URN, Visual Library page, number of pages in the full-text index."
"compact-memory-pages.ttl.gz" = "Volumes, issues and pages: for every page its issue, sequence, label and image in the Visual Library; for every volume and issue its parent, journal, label and date."

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "f34385ab4df6146a8e2c3e5416e04a6a689a8a4b"
description = "The whole corpus of the full-text index: 336 journals from the MODS records, 88,691 volumes, issues and articles (classes from schema.org where the page table gives the kind), 846,499 pages (jl:Page) with their images. Compared with 2021-01-18, 4,710 triples are no longer stated (second IRIs of 2,060 pages, 3 pages not in the index, journal titles as jl:title and journal-level images, 16 nodes assigned to a second record of their journal; see the generator README)."

  [[versions.files]]
  path = "compact-memory-journals.ttl.gz"
  bytes = 29084
  sha256 = "daf0e11224f463a0fe7b304a188261cb78145d439c584d3aedfa1de2475a102b"
  triples = 3707

  [[versions.files]]
  path = "compact-memory-pages.ttl.gz"
  bytes = 11842228
  sha256 = "f6a8f335d9fc4e7b03c9ac9b29eabc3f81307f1fe382682701caaef251fef04c"
  triples = 4549427

  [[versions.files]]
  path = "compact-memory-meta.ttl.gz"
  bytes = 3146
  sha256 = "d1c056e70fdd40e3696bf2f609ff84dd0c14d6d168ba52ef8ff79e7539659e2b"
  triples = 76

[[versions]]
version = "2021-01-18"
issued = "2021-01-18"
author = "Marco Rovera"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "cm_tagme_pages.ttl.gz"
  bytes = 3908853
  sha256 = "6c6bbedb82547dd4b06d8969760b312a03b0b7233b6b6620e334a8d69adb0874"

  [[versions.files]]
  path = "compact-memory-meta.ttl.gz"
  bytes = 1719
  sha256 = "e7fa6e8d66f2ff6f263035dc5c4123f7f96b073c7f967aef47e63369d7945dec"
  triples = 58

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "New version from the framework generator: the whole Compact Memory corpus (journals, volumes, issues, all pages of the full-text index), with classes; the version 2021-01-18 covered only pages with entity mentions."

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Generator ported from Jupyter notebooks to Python scripts (judaicalink-generators); the published version was not regenerated."
+++
The Compact Memory corpus of UB Frankfurt (Jewish periodicals in German-speaking countries) as linked data: its journals, their volumes and issues, and the pages of the full-text index, with links to the journal pages and page images in the Visual Library.

<!--more-->

Journal descriptions come from the MODS records of UB Frankfurt (export of 15 June 2020), the structure of volumes,
issues and pages from its page table (compact-memory-supp). Since 2026 the dataset describes every page of the
full-text index of the FID portal; the version of 2021 described only the pages on which entities had been found
(see cm-tagme), and its page IRIs are kept. Page IRIs have the form
`<journal>-<volume>-<issue>--<file prefix>-<page VLID>`; the page VLID is the document id of the full-text index, and
the page image is `http://sammlungen.ub.uni-frankfurt.de/cm/periodical/pageview/<VLID>`.
