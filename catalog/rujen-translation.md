+++
slug = "rujen-translation"
title = "Translations for Rujen (Google)"
author = "Kai Eckert"
date = "2020-09-28"
website = "http://www.rujen.ru"
example = "http://data.judaicalink.org/data/rujen/ben-gurion"
picture = "/img/rujen_logo.png"
namespaces = ["rujen"]
aliases = ["/encyclopediae/encyclopediae-of-russion-jewry/", "/datasets/encyclopediae-of-russion-jewry/"]
stable = "2020-09-28"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/rujen-translation"

[[versions]]
version = "2020-09-28"
issued = "2020-09-28"
author = "Kai Eckert"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "rujen-en-abstract-translations.ttl"
  bytes = 17238866
  sha256 = "856b871da06ebc338095f945ac79e9011db52475db6ae541fc4deb8adf7ba5ec"

  [[versions.files]]
  path = "rujen-en-label-translations.ttl"
  bytes = 1531668
  sha256 = "01d0e12173a9d03759da2c016ec887e3f88f48d9766140acdfd1f9edd847aa93"

  [[versions.files]]
  path = "rujen-de-abstract-translations.ttl"
  bytes = 17807166
  sha256 = "f507eb37509345598ee09089256c459ab89ad3899196ffd1aff2320a09c95a55"

  [[versions.files]]
  path = "rujen-de-label-translations.ttl"
  bytes = 1534116
  sha256 = "e3e70a8bbe6c1a572122cba5eb34a9402d90e829ba281d288a74845daab06465"

  [[versions.files]]
  path = "rujen-translation-meta.ttl.gz"
  bytes = 1871
  sha256 = "6601e71f49ddc9aad973a872fcdacaa283d424cbbe5d74b6b111e426e1409997"
  triples = 85

[[changelog]]
date = "2026-10-11"
version = "2020-09-28"
author = "Kai Eckert"
text = "Self-description written by the labs generator (rujen-translation-metadata.ttl) removed from the version; the generated -meta file takes its place. Its generation time and commit are documented in the generator folder."
refs = ["0018"]
+++

Automatic translation of abstracts and preferred labels to English and German using Google Translate.
