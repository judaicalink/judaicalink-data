+++
slug = "geo-coordinates"
title = "Geographical Coordinates"
author = "Kai Eckert"
date = "2018-10-04"
example = "http://data.judaicalink.org/data/Aachen"
namespaces = ["geo-coordinates"]
stable = "2026-09-26"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[files]
"city-geocoor-05.ttl.gz" = "Geographical Coordinates of Cities"

[[versions]]
version = "2026-09-26"
issued = "2018-10-04"
author = "Maral Dadvar"
authorlink = "http://wiss.iuk.hdm-stuttgart.de/people/maral-dadvar"
graph = "http://data.judaicalink.org/data/geo-coor"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "city-geocoor-05.ttl.gz"
  bytes = 142001
  sha256 = "c4fdf74620e2023a938bbab11103b1af87c5cef0daf5f8ae40b0c74d1ab18004"

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++

 This dataset contains all the geo-coordinates of all the cities which are stated in the JudaicaLink datasets either as birth location or death location. All these coordinates as well as their GND-ids are extracted from GND entries of the corresponding cities when available. 
