+++
slug = "haskala"
title = "The Library of Haskala"
author = "Kai Eckert"
date = "2019-07-01"
website = "https://www.haskala-library.net/"
example = "http://data.judaicalink.org/data/haskala/person/28"
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
commit = "4617329de6dedf1425693b95ab83a76a7ba9f66d"
description = "Made from the Drupal database of the Library of Haskala (dump of 2015-04-20): all 1,980 persons, 525 books, editions, mentions, productions, prefaces, translations and 809 taxonomy terms with all their fields, and the schema of the database; the 2019 IRIs replaced; the haskala.net persons of 2019 kept."

  [[versions.files]]
  path = "haskala-gnd-2019.ttl.gz"
  bytes = 1257
  sha256 = "1d96ec95b4954865b0c2a912e5db1fc9ce352328b6eb4b07a9ef7c6afcd7f0f7"
  triples = 125

  [[versions.files]]
  path = "haskala-net.ttl.gz"
  bytes = 5941
  sha256 = "d2b6283f9ea5e15d426aeaa2ecbb983d4afd3389ca9d43762c471457e92c7cbc"
  triples = 771

  [[versions.files]]
  path = "haskala-vocabulary.ttl.gz"
  bytes = 11694
  sha256 = "93db5319dfaac0467134197a7b29c2c06ddcdf0c4a5e7d0df63bd043392e8430"
  triples = 2779

  [[versions.files]]
  path = "haskala.ttl.gz"
  bytes = 871677
  sha256 = "03c3c988a5abf8cd72c3fa9f963345cfa3798f77f8c5ce3482e900a874d26b2a"
  triples = 73745

  [[versions.files]]
  path = "haskala-meta.ttl.gz"
  bytes = 3116
  sha256 = "567dd0e1acef113cfde0357f15bece2ee5945be21fc18e3c0be5533707c940c1"
  triples = 101

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
text = "Version 2026-10-12 (from the database) made the stable version; example IRI of that version."

[[changelog]]
date = "2026-10-13"
version = "2026-10-12"
author = "Kai Eckert"
text = "Made again from the source (decisions 0024, 0026): the Drupal database of haskala-library.net (dump of 2015-04-20, content tables only), true to the database: 5,657 nodes of seven content types (1,980 persons, 525 books, 327 editions, 1,867 mentions, 667 productions, 272 prefaces, 19 translations), 809 terms of 19 taxonomies, 39,225 field values, and the schema (haskala-vocabulary.ttl.gz: classes and properties in data/haskala/vocab/ with labels, types, targets and order). Persons foaf:Person with VIAF links (583), books jl:Work, cities jl:Place with coordinates. The 194 library persons of 2019 are dcterms:isReplacedBy their nodes (5 by two duplicate nodes), their GND links carried over (125); the 32 haskala.net persons keep their IRIs and 2019 data, with their occupations. Made by generators/haskala/generate.py."
+++

The Library of Haskala contains 525 books in German and Hebrew identified by leading scholars as Haskala literature,
with the persons who wrote, translated, printed, funded or are mentioned in them.

<!--more-->

The data comes from a German-Israeli research project (2004–2010) headed by Shmuel Feiner (Bar-Ilan University),
Zohar Shavit (Tel Aviv University) and Christoph Schulte (University of Potsdam). Its database was published as
haskala-library.net, hosted by the Judaica Division of the Frankfurt University Library.
Since version 2026-10-12, the dataset holds the whole database: persons, books with their bibliographical and
material description, editions, prefaces, translations, the persons mentioned in the books and their roles, and the
taxonomies (places, publishers, topics, languages, …), together with a description of its schema.
Version 2019-07-01 held the persons only, enriched with GND data; it also includes 32 persons of the Haskala
biographies of the University of Potsdam (haskala.net), which the current version keeps.
