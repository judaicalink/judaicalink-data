+++
slug = "haskala"
title = "The Library of Haskala"
author = "Kai Eckert"
date = "2019-07-01"
website = "https://www.haskala-library.net/"
example = "http://data.judaicalink.org/data/haskala/Ascher_Saul"
namespaces = ["haskala"]
stable = "2026-10-12"
kind = "records"
method = ["scraped", "converted", "lookup", "curated"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/haskala"

[[versions]]
version = "2026-10-12"
issued = "2026-10-12"
author = "Kai Eckert"
commit = "b8b3dc528ae97874d36000a353cc20ea88c6c19e"
description = "Made from 2019-07-01 (the enriched version) with the occupations of the haskala.net persons, which the 2019 enrichment dropped, and without empty values."

  [[versions.files]]
  path = "haskala.ttl.gz"
  bytes = 36055
  sha256 = "53f95a1ea19b8b8d0ac1702f52a41b23ba8776b6d2737ed1f2ac42c299d54c5b"
  triples = 3899

  [[versions.files]]
  path = "haskala-meta.ttl.gz"
  bytes = 1668
  sha256 = "b7511063cccea2535d60878cdb0de083b721ff2e4d86e4c5d127e099d093d089"
  triples = 66

[[versions]]
version = "2025-03-24"
issued = "2025-03-24"
author = "Benjamin Schnabel"
description = "Regenerated; the persons are split into Haskala.ttl and Haskala_net.ttl (only the first was in the catalogue before). Most birth and death dates and places of the version of 2019 are missing, so 2019-07-01 stays the stable version."

  [[versions.files]]
  path = "Haskala.ttl.gz"
  bytes = 19519
  sha256 = "c167c1ef7719d90963c0b5d2ffb01cb4c62ce9c7f95670e38e2a46d2fa7dff85"

  [[versions.files]]
  path = "Haskala_net.ttl.gz"
  bytes = 2824
  sha256 = "79a450e29adb2cfc747f9ba5b8bde98901f657c05c74af7f3af15ce3d3b538b1"

  [[versions.files]]
  path = "haskala-meta.ttl.gz"
  bytes = 1959
  sha256 = "5b36ba3558ff0b66421ba12563d242c3d0df4fdaa4dce3612dbd2328e76dbe26"
  triples = 73

[[versions]]
version = "2019-07-01"
issued = "2019-07-01"
author = "Maral Dadvar"
description = "The enriched version of 2019, with birth and death dates and places."

  [[versions.files]]
  path = "Haskala_enriched.ttl.gz"
  bytes = 34911
  sha256 = "b024ce78236af00ba1480dd63eff33a5f42e0c22c8c0251b0e760fb7e7d7049b"

  [[versions.files]]
  path = "haskala-meta.ttl.gz"
  bytes = 1793
  sha256 = "e15825ccd240cc7557b5aef1c5a0488228971fa530a60bec5614e503d36d1303"
  triples = 62

[[changelog]]
date = "2026-10-12"
author = "Kai Eckert"
text = "Version 2026-10-12 made the stable version (it keeps all data of 2019-07-01 and adds the haskala.net occupations)."

[[changelog]]
date = "2026-10-12"
version = "2026-10-12"
author = "Kai Eckert"
text = "New version made from 2019-07-01 (decision 0024): the occupations of 30 haskala.net persons added from Haskala_net.ttl of 2025-03-24 as jl:occupation, one value per occupation (75); 12 empty dates and places dropped. Made by generators/haskala/generate.py."
+++

The Library of Haskala contains 525 books in German and Hebrew identified by leading scholars as Haskala literature. 

<!--more-->

The database is hosted and run by the Judaica Division of the Frankfurt University Library.
We have extracted the author's information from this database, and the created dataset was further enriched with the corresponding GND information of each author. 
