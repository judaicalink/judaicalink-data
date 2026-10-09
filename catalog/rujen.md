+++
slug = "rujen"
title = "Encyclopedia of Russian Jewry"
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
path = "generators/rujen"

[files]
"rujen.jsonl.gz" = "Raw data crawled from rujen.ru, input of the generator."

[[versions]]
version = "2020-09-28"
issued = "2020-09-28"
author = "Kai Eckert"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "rujen-metadata.ttl.gz"
  bytes = 603
  sha256 = "5a2ca1ebe6db58a564551b379af6a257599c07a680d72680a9fd251ecb0bed9d"

  [[versions.files]]
  path = "rujen.ttl.gz"
  bytes = 6783508
  sha256 = "66b4fed0d221d93c85ee58934365310bc8fd230a4b15729362d3be2f7e8f7c82"

  [[versions.files]]
  path = "rujen.jsonl.gz"
  bytes = 7829862
  sha256 = "2ded560739a06d39eee86c0506aa093d961a144491a246efc09755f1d49b3d6e"

[[changelog]]
date = "2025-06-05"
author = "Benjamin Schnabel"
text = "Encyclopedia converters rewritten in Python (judaicalink-generators); the archived version was not regenerated."

[[changelog]]
date = "2018-10-22"
author = "Maral Dadvar"
text = "Revised version in Turtle (rujen.ttl.gz)."

[[changelog]]
date = "2016-09-12"
author = "Kai Eckert"
text = "First version (rujen.n3.gz; date of the first catalogue listing)."
+++

Rujen.ru provides an Internet version of the Encyclopedia of Russian Jewry, which is published in Moscow since 1994, giving a comprehensive, objective picture of the life and activity of the Jews of Russia, the Soviet Union and the CIS.
<!--more-->

The encyclopedia is structurally divided into three parts: 1. biographical information, 2. local history of the Jewish community in pre-revolutionary Russia, the Soviet Union and the CIS, and 3. thematic information on concepts related to Jewish civilization, the contribution of the Jews of Russia in various fields of activity, various Jewish social, scientific, cultural organizations, etc. The originally published volumes contain more than 10,000 biographies and more than 10,000 place names. The electronic version contains corrections and additions in the form of new articles.

Counts in the former catalogue entry: concepts: 20,434; links: 30,052.
