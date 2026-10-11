+++
slug = "epidat"
title = "Epidat - Epigraphical Database"
author = "Kai Eckert"
date = "2022-06-29"
website = "http://www.steinheim-institut.de/wiki/index.php/Epidat"
example = "http://data.judaicalink.org/data/epi/AbrahamGottschalk"
namespaces = ["epi"]
stable = "2023-07-14"
kind = "records"
method = ["converted", "rule-based"]

[license]
name = "CC4.0"
uri = "https://creativecommons.org/licenses/by/4.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/epidat"

[[versions]]
version = "2023-07-14"
issued = "2023-07-14"
author = "Benjamin Schnabel"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "epidat-final-01.ttl.gz"
  bytes = 1533441
  sha256 = "0aea2e25ff18d0fa193b62a49ce923bcd5dcc87732d81b38350f0011b166718a"

  [[versions.files]]
  path = "epidat-meta.ttl.gz"
  bytes = 2129
  sha256 = "a2f136e5bdd7af7d5859d31c107a41e2b3b049681dcb69274e51b5c06ef4b22e"
  triples = 56

[[changelog]]
date = "2022-06-29"
author = "Benjamin Schnabel"
text = "First version."
+++
Epidat is an epigraphical database of the [Steinheim institute](http://www.steinheim-institut.de) for jewish tombstones in Germany.

It serves as inventory, for documentation, edition and for presentation of epigraphical data.
Currently, there are 228 digital editions with 39,998 tombstones (79,698 image files) online accessible.
The archive in development and maintenance by Thomas Kollatz.

<!--more-->

Epidat is a research platform for jewish tombstone epigraphy in Germany.
The database for jewish tombstone epigraphy serves as inventory, for documentation, edition and for presentation of epigraphical data.
There are 249 digital editions with 46,257 tombstones (83,126 image files) online accessible as digital edition.
Not accessible are 1479 datasets for tombstones which have been erected after the year 1952.

Since March 2019 epidat is being developed continuously as scientific research cooperation between the Salomon-Ludwig-Steinheim-Institute, Essen and the Academy of Science and Literature, Mainz.

Currently, there are two options to access the tombstones, inscriptions, person data and extensive image material which are edited in epidat. One option is the web interface which has not bein changed since 2006. Parallel an epidat BETA version is being developed, with new features, bilingual menus and optimized for mobile devices.
