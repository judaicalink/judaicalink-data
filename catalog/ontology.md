+++
slug = "ontology"
title = "JudaicaLink Ontology"
author = "Kai Eckert"
date = "2025-07-09"
website = "http://ontology.judaicalink.org"
example = "http://data.judaicalink.org/ontology/describedAt"
namespaces = ["ontology"]
stable = "2025-11-27"
kind = "ontology"
method = ["curated"]

[license]
name = "CC BY 4.0"
uri = "https://creativecommons.org/licenses/by/4.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/ontology"

[[versions]]
version = "2025-11-27"
issued = "2025-11-27"
author = "Benjamin Schnabel"
description = "The ontology as of judaicalink-ontology b26c961, as served on ontology.judaicalink.org."

  [[versions.files]]
  path = "judaicalink-ontology.ttl.gz"
  bytes = 2802
  sha256 = "272c3c59db7b705a452793f8c152e7e739e79d17383f56a1fdb68af9315af09a"

  [[versions.files]]
  path = "ontology-meta.ttl.gz"
  bytes = 1710
  sha256 = "21762f0fca59f12e4326358643be3cac98db973d49409ac306143e31138561c8"
  triples = 57

[[changelog]]
date = "2026-10-12"
author = "Kai Eckert"
text = "Licence name corrected to CC BY 4.0 (was \"CC4.0\"); the licence URI is unchanged."

[[changelog]]
date = "2020-09-29"
author = "Kai Eckert"
text = "Turtle file generated from the documentation."

[[changelog]]
date = "2018-07-26"
author = "Maral Dadvar"
text = "Ontology updated."

[[changelog]]
date = "2018-07-24"
author = "Kai Eckert"
text = "First version of the ontology documentation (judaicalink-ontology)."
+++
[JudaicaLink Ontology](https://ontology.judaicalink.org) This dataset provides the ontology for JudaicaLink. <!--more-->
It is used to describe the data in the JudaicaLink project, which includes various aspects of Jewish cultural heritage, such as texts, objects, and places.
The ontology is available in Turtle format and can be accessed through the provided URL. It is designed to be used with the JudaicaLink data, which is available in various formats, including RDF and JSON-LD.
