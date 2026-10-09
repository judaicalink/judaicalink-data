+++
slug = "rujen-translation"
title = "Translations for Rujen (Google)"
author = "Kai Eckert"
date = "2020-09-28"
website = "http://www.rujen.ru"
example = "http://data.judaicalink.org/data/rujen/ben-gurion"
picture = "/img/rujen_logo.png"
namespaces = ["rujen"]
inputs = ["rujen-translation-supp"]
aliases = ["/encyclopediae/encyclopediae-of-russion-jewry/", "/datasets/encyclopediae-of-russion-jewry/"]
stable = "2026-09-26"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/wisslab/judaicalink-labs"
path = "labs/data/management/commands/generate_rujen_translation.py"

[[versions]]
version = "2026-09-26"
issued = "2020-09-28"
author = "Kai Eckert"
authorlink = "http://wiss.iuk.hdm-stuttgart.de/people/kai-eckert"
commit = "39f04c243cacadc2d12e602a8b1b0929d115413a"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "rujen-translation-metadata.ttl"
  bytes = 1350
  sha256 = "92007443ea840f58e4565279269dd49e66841906f4b7d9d09d4aaa0bba0d5962"

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

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++

Automatic translation of abstracts and preferred labels to English and German using Google Translate.
