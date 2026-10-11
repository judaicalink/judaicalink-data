+++
slug = "geo-coordinates"
title = "Geographical Coordinates"
author = "Kai Eckert"
date = "2018-10-04"
example = "http://data.judaicalink.org/data/Aachen"
namespaces = ["geo-coordinates"]
stable = "2018-08-08"

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/geo-coordinates"

[files]
"city-geocoor-05.ttl.gz" = "Geographical Coordinates of Cities"

[[versions]]
version = "2018-08-08"
issued = "2018-08-08"
author = "Maral Dadvar"
graph = "http://data.judaicalink.org/data/geo-coor"
description = "Data files of the catalogue state judaicalink-site 81b42a5 (the state Frankfurt loaded)."

  [[versions.files]]
  path = "city-geocoor-05.ttl.gz"
  bytes = 142001
  sha256 = "c4fdf74620e2023a938bbab11103b1af87c5cef0daf5f8ae40b0c74d1ab18004"

  [[versions.files]]
  path = "geo-coordinates-meta.ttl.gz"
  bytes = 1625
  sha256 = "d7384a36624d6a4f5f74e1e5f94c671729d84b44deacab5ea588d7668d1baf27"
  triples = 55
+++

 This dataset contains all the geo-coordinates of all the cities which are stated in the JudaicaLink datasets either as birth location or death location. All these coordinates as well as their GND-ids are extracted from GND entries of the corresponding cities when available. 
